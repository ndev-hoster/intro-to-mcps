import os
from google import genai
from dotenv import load_dotenv
import anthropic
from mcp.client.stdio import stdio_client
from utils import *


load_dotenv()

def make_it(user_request):
    ######### Agent initializations #########
    gem_key = os.environ.get("GEMINI_API_KEY")
    MANAGER = genai.Client(api_key=gem_key)

    QA = genai.Client(api_key=gem_key)

    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    DEV = anthropic.Anthropic()

    ######### Tool definitions #########
    # dev_tools = list of tools from the dev_tools mcp
    # qa_tools = list of tools from the dev_tools mcp

    ######### Persona loading #########
    manager=load_persona("manager")
    developer=load_persona("developer")
    qa=load_persona("tester")

    ######### Development loop #########
    mgr_response = MANAGER.models.generate_content(
    model='gemini-3-flash-preview',
    contents=user_request,
    config=types.GenerateContentConfig(
        system_instruction=manager,
        temperature=0.7,
        ),
    ).text
    
    dev_response = DEV.howeverweuseclaudeSDK(mgr_response,developer)
    qa_response = QA.models.generate_content(
    model='gemini-3-pro-preview',
    contents=user_request,
    config=types.GenerateContentConfig(
        system_instruction=qa + "\n Manager's Spec: \n"+mgr_response,
        tools=[qa_tools_from_mcp],
        temperature=0.1,
        ),
    ).text


    BUGS_FOUND = None

    if qa_response.text.contains("FAILED"):
        BUGS_FOUND = True
    else:
        BUGS_FOUND = False


    while BUGS_FOUND:
        dev_response = DEV.howeverweuseclaudeSDK(mgr_response,developer)
        qa_response = None #reiterate on this


    QA.close()
    DEV.close()


if __name__ == "__main__":
    request=input("What do you want to make today?")
    make_it(request)