import os
from google import genai
from dotenv import load_dotenv
import anthropic

load_dotenv()

######### Agent initializations #########
gem_key = os.environ.get("GEMINI_API_KEY")
QA = genai.Client(api_key=gem_key)

claude_key = os.environ.get("ANTHROPIC_API_KEY")
DEV = anthropic.Anthropic()

qa_response = QA.models.list()
print("Gemini models:")
for model in qa_response:
    print(model.name)
print('#'*50)

dev_response = DEV.models.list()
print("Claude models:")
for model in dev_response.data:
    print(model.id)



QA.close()
DEV.close()