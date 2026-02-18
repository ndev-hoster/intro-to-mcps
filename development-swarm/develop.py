import asyncio
import os
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
GEMINI_MODEL = "gemini-2.5-pro"


# -------------------------------------------------------
# DEV LOOP (Claude)
# -------------------------------------------------------

async def run_dev(prompt, mcp_session, gemini, system_prompt):
    contents = [prompt]
    iteration = 0

    while True:
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

        # If no function call → we’re done
        if not resp.function_calls:
            logging.info("No function call returned. Final answer reached.")
            logging.info(f"Final text: {resp.text}")
            return resp.text

        call = resp.function_calls[0]

        logging.info(f"Function call detected: {call.name}")
        logging.info(f"Arguments: {json.dumps(call.args, indent=2)}")

        result = await mcp_session.call_tool(call.name, call.args)

        logging.info(f"Tool returned: {result.content}")

        contents.extend([
            resp.candidates[0].content,
            types.Part.from_function_response(
                name=call.name,
                response={"result": result.content[0].text}
            )
        ])

        # 🛑 Emergency brake
        if iteration > 20:
            logging.error("Max iterations reached. Breaking loop.")
            return "Error: Too many tool calls (possible infinite loop)."



# -------------------------------------------------------
# QA LOOP (Gemini)
# -------------------------------------------------------

async def run_qa(prompt, mcp_session, gemini, system_prompt):
    contents = prompt
    tool_list = await mcp_session.list_tools()
    tools = tool_list.tools
    while True:
        resp = gemini.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
        config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.1,
        tools=tools
    ),
        )

        if not resp.function_calls:
            return resp.text

        call = resp.function_calls[0]
        result = await mcp_session.call_tool(call.name, call.args)

        contents = [
            prompt,
            resp.candidates[0].content,
            GeminiTypes.Part.from_function_response(
                name=call.name,
                response={"result": result.content[0].text}
            )
        ]


# -------------------------------------------------------
# SWARM ENTRY POINT
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

    # --- Start MCP sessions using official async context pattern ---
    async with stdio_client(dev_params) as (dev_read, dev_write), \
               stdio_client(qa_params) as (qa_read, qa_write):

        async with ClientSession(dev_read, dev_write) as dev_mcp, \
                   ClientSession(qa_read, qa_write) as qa_mcp:

            await dev_mcp.initialize()
            await qa_mcp.initialize()

            # 1️⃣ Manager creates spec (Gemini)
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

            # 2️⃣ Developer builds using Claude + dev MCP tools
            dev_output = await run_dev(
                spec,
                dev_mcp,
                gemini,
                developer_prompt
            )

            print("\nDeveloper Output:\n", dev_output)

            # 3️⃣ QA evaluates using Gemini + qa MCP tools
            qa_input = f"""
                {qa_prompt}

                Manager Spec:
                {spec}

                Developer Output:
                {dev_output}
                """

            qa_output = await run_qa(
                qa_input,
                qa_mcp,
                gemini,
                qa_prompt
            )

            print("\nQA Result:\n", qa_output)

            # 4️⃣ Iterative refinement loop
            iteration = 0
            MAX_ITERS = 3

            while "FAILED" in qa_output and iteration < MAX_ITERS:
                iteration += 1
                print(f"\n🔁 Iteration {iteration}")

                dev_output = await run_dev(
                    spec + "\nFix QA issues.",
                    dev_mcp,
                    gemini,
                    developer_prompt
                )

                qa_input = f"""
                    {qa_prompt}

                    Manager Spec:
                    {spec}

                    Developer Output:
                    {dev_output}
                    """

                qa_output = await run_qa(
                    qa_input,
                    qa_mcp,
                    gemini,
                    qa_prompt
                )

            print("\nFinal QA Result:\n", qa_output)

    # clients
    claude = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    gem_key = os.environ.get("GEMINI_API_KEY")
    gemini = genai.Client(api_key=gem_key)

    # personas
    manager_prompt = load_persona("manager")
    developer_prompt = load_persona("developer")
    qa_prompt = load_persona("tester")

    # MCP sessions (must live INSIDE make_it)
    async with stdio_client(["python", "mcps/dev_tools.py"]) as dev_server, \
               stdio_client(["python", "mcps/qa_tools.py"]) as qa_server:

        dev_mcp = ClientSession(dev_server)
        qa_mcp = ClientSession(qa_server)

        await dev_mcp.initialize()
        await qa_mcp.initialize()

        try:
            # 1️⃣ Manager spec (Gemini)
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

            # 2️⃣ Dev builds
            dev_output = await run_dev(spec, dev_mcp, gemini, developer_prompt)
            print("\nDeveloper Output:\n", dev_output)

            # 3️⃣ QA evaluates
            qa_input = f"{qa_prompt}\nManager Spec:\n{spec}\nDeveloper Output:\n{dev_output}"
            qa_output = await run_qa(qa_input, qa_mcp, gemini, qa_prompt)

            print("\nQA Result:\n", qa_output)

            # 4️⃣ Simple pass/fail loop
            iteration = 0
            MAX_ITERS = 3

            while "FAILED" in qa_output and iteration < MAX_ITERS:
                iteration += 1
                print(f"\n🔁 Iteration {iteration}")

                dev_output = await run_dev(
                    spec + "\nFix QA issues.",
                    dev_mcp,
                    gemini,
                    developer_prompt
                )

                qa_input = f"{qa_prompt}\nManager Spec:\n{spec}\nDeveloper Output:\n{dev_output}"
                qa_output = await run_qa(qa_input, qa_mcp, gemini, qa_prompt)

            print("\nFinal QA Result:\n", qa_output)

        finally:
            await dev_mcp.close()
            await qa_mcp.close()



# -------------------------------------------------------
# CLI ENTRY
# -------------------------------------------------------

if __name__ == "__main__":
    # user_input = input("What do you want to build today? > ")
    user_input = "A cli based calculator that evaluates whatever expression I put into it."
    asyncio.run(make_it(user_input))
