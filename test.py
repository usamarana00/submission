from openai import OpenAI
import os
from dotenv import load_dotenv
import json
load_dotenv()
print("API Key:", os.getenv("OPENAI_API_KEY"))


with open("config.json", "r") as f:
    config = json.load(f)

api_key = config.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found in config file.")

client = OpenAI(api_key=api_key)
def test_openai_api_key():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "i love working on super mario.  what do you think?."
            }
        ]
    )

    print(completion.choices[0].message)


# Run the test
test_openai_api_key()
