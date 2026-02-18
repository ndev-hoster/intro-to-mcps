import asyncio
import os
import sys
import shutil
import subprocess
from dotenv import load_dotenv
import logging
import json
from anthropic import Anthropic
from google import genai
from google.genai import types
from mcp.client.stdio import stdio_client
from mcp import ClientSession

from utils import load_persona

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
load_dotenv()

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------

CLAUDE_MODEL = "claude-opus-4-6"
GEMINI_MODEL = "gemini-2.5-flash"

# -------------------------------------------------------
# QA LOOP (Gemini)
# -------------------------------------------------------

async def run_qa(prompt, mcp_session, gemini, system_prompt):
    contents = prompt
    tool_list = await mcp_session.list_tools()
    tools = tool_list.tools
    iteration = 0
    MAX_QA_ITERATIONS = 15
    logging.info(f"QA Started Testing....")

    while iteration < MAX_QA_ITERATIONS:
        iteration += 1
        resp = gemini.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                tools=tools
            ),
        )

        # Check if QA has finished (looks for STATUS in response)
        if resp.text and "STATUS:" in resp.text.upper():
            logging.info(f"[QA] Final response detected: {resp.text}")
            return resp.text
        
        # If no function call → also done
        if not resp.function_calls:
            return resp.text

        call = resp.function_calls[0]
        result = await mcp_session.call_tool(call.name, call.args)
        
        if resp.text:
            logging.info(f"[QA] Response: {resp.text}")

        logging.info(f"[QA] Tool: {call.name}")
        logging.info(f"[QA] Args: {json.dumps(call.args, indent=2)}")
        logging.info(f"[QA] Result: {result.content[0].text[:200]}")
        
        contents = [
            prompt,
            resp.candidates[0].content,
            types.Part.from_function_response(
                name=call.name,
                response={"result": result.content[0].text}
            )
        ]
    
    logging.warning("QA max iterations reached")
    return "STATUS: FAIL - QA evaluation incomplete (max iterations reached)"


# -------------------------------------------------------
# DEV LOOP (Gemini)
# -------------------------------------------------------

async def run_dev(prompt, mcp_session, gemini, system_prompt):
    allowed_commands = ["python"]
    contents = [prompt]
    iteration = 0
    MAX_DEV_ITERATIONS = 20  # Safety limit

    while iteration < MAX_DEV_ITERATIONS:
        iteration += 1
        logging.info(f"[ITERATION {iteration}] Sending to Gemini")
        logging.info(f"Current contents length: {len(contents)}")

        tool_list = await mcp_session.list_tools()

        resp = gemini.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                tools=tool_list.tools
            ),
        )

        # If no function call → we're done
        if not resp.function_calls:
            logging.info("No function call returned. Final answer reached.")
            logging.info(f"Final text: {resp.text}")
            return resp.text

        call = resp.function_calls[0]

        logging.info(f"Function call detected: {call.name}")
        logging.info(f"Arguments: {json.dumps(call.args, indent=2)}")

        if call.name == "custom_command" and call.args.get("command").split(" ")[0] not in allowed_commands:
            command = call.args.get("command")
            print(f"\n⚠️ Command requested:\n{command}")
            decision = input("Approve? [y/n]: ").strip().lower()

            if decision != "y":
                tool_result_text = "Command blocked by user."
            else:
                try:
                    proc = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    tool_result_text = proc.stdout + proc.stderr
                    if not tool_result_text.strip():
                        tool_result_text = "Command executed successfully."
                except Exception as e:
                    tool_result_text = f"Execution error: {str(e)}"
        else:
            result = await mcp_session.call_tool(call.name, call.args)
            tool_result_text = result.content[0].text

        logging.info(f"Tool returned: {tool_result_text}")

        contents.extend([
            resp.candidates[0].content,
            types.Part.from_function_response(
                name=call.name,
                response={"result": tool_result_text}
            )
        ])

    logging.error("Max dev iterations reached. Breaking loop.")
    return "Error: Too many tool calls (possible infinite loop)."


# -------------------------------------------------------
# SWARM ENTRY POINT (CLEANED UP)
# -------------------------------------------------------

async def make_it(user_request):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    # --- Load API keys ---
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    gem_key = os.environ.get("GEMINI_API_KEY")

    # --- Initialize LLM clients ---
    claude = Anthropic(api_key=claude_key)
    gemini = genai.Client(api_key=gem_key)

    # --- Load personas ---
    manager_prompt = load_persona("manager")
    developer_prompt = load_persona("developer")
    qa_prompt = load_persona("tester")

    # --- Define MCP server launch parameters ---
    dev_params = StdioServerParameters(
        command="python",
        args=["mcps/dev_tools.py"],
        env=None
    )

    qa_params = StdioServerParameters(
        command="python",
        args=["mcps/qa_tools.py"],
        env=None
    )

    # --- Start MCP sessions ---
    async with stdio_client(dev_params) as (dev_read, dev_write), \
               stdio_client(qa_params) as (qa_read, qa_write):

        async with ClientSession(dev_read, dev_write) as dev_mcp, \
                   ClientSession(qa_read, qa_write) as qa_mcp:

            await dev_mcp.initialize()
            await qa_mcp.initialize()

            # 1️⃣ Manager creates spec
            mgr_resp = gemini.models.generate_content(
                model="gemini-3-flash-preview",
                contents=user_request,
                config={
                    "system_instruction": manager_prompt,
                    "temperature": 0.7
                }
            )

            spec = mgr_resp.text
            print("\nManager Spec:\n", spec)

            # 2️⃣ Developer builds
            dev_output = await run_dev(spec, dev_mcp, gemini, developer_prompt)
            print("\nDeveloper Output:\n", dev_output)

            # 3️⃣ QA evaluates
            qa_input = f"""
                Manager Spec:
                {spec}

                Developer Output:
                {dev_output}

                Please test the code and report any issues.
            """

            qa_output = await run_qa(qa_input, qa_mcp, gemini, qa_prompt)
            print("\nQA Result:\n", qa_output)

            # 4️⃣ Iterative refinement loop
            iteration = 0
            MAX_ITERS = 10

            # Check for common failure indicators
            while iteration < MAX_ITERS and any(keyword in qa_output.lower() for keyword in ['fail', 'error', 'issue', 'bug', 'problem']):
                iteration += 1
                print(f"\n🔁 Iteration {iteration}")

                dev_output = await run_dev(
                    f"{spec}\n\nQA Feedback:\n{qa_output}\n\nFix all reported issues.",
                    dev_mcp,
                    gemini,
                    developer_prompt
                )

                qa_input = f"""
                    Manager Spec:
                    {spec}

                    Developer Output:
                    {dev_output}

                    Please test the code and report any issues.
                """

                qa_output = await run_qa(qa_input, qa_mcp, gemini, qa_prompt)
                print(f"\nQA Result (Iteration {iteration}):\n", qa_output)

            print("\n✅ Final QA Result:\n", qa_output)

# -------------------------------------------------------
# CLI ENTRY
# -------------------------------------------------------

def cleanup():
    if os.path.exists("dev-space/"):
        shutil.rmtree("dev-space/")
    if os.path.exists("qa-space/"):
        shutil.rmtree("qa-space/")

    os.makedirs("dev-space/")
    os.makedirs("qa-space/")
    print("############# Cleanup of directories successful #############")
async def main():
    user_input = "A cli based calculator that evaluates whatever expression I put into it, for simple BODMAS ops only"
    cleanup()
    await make_it(user_input)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Shutting down gracefully...")
        sys.exit(0)