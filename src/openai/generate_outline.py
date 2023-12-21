import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gpt-3.5-turbo-1106"
PAYLOAD_PATH = f"src/data/chat/payloads"
REPLY_PATH = f"src/data/chat/replies"

SYSTEM_CONTEXT_TEMPLATE = open("src/data/prompts/pre-outline-system.md", "r").read()
OUTLINE_TEMPLATE = open("src/data/prompts/outline.md", "r").read()


def generate_course_outline(course_name: str) -> OpenAI:
    folder_name = course_name.lower().replace(" ", "-")
    save_file_name = course_name.lower().replace(" ", "-")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Build initial message payload
    system_prompt = SYSTEM_CONTEXT_TEMPLATE.format(course_name=course_name)
    outline_prompt = OUTLINE_TEMPLATE.format(course_name=course_name)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": outline_prompt}
    ]

    completion = None
    try:
        # Send to ChatGPT
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
    except Exception as e:
        print(f"Error: {e}")
        return None

    # Save payload and reply
    payload_file = f"{PAYLOAD_PATH}/{folder_name}/{save_file_name}-outline.json"
    outline_file = f"{REPLY_PATH}/{folder_name}/{save_file_name}-outline.md"

    with open(payload_file, 'w') as f:
        f.write(completion.model_dump_json())
        f.close()

    outline_content = completion.choices[0].message.content
    with open(outline_file, 'w') as f:
        f.write(outline_content)
        f.close()

    print(colored(f"Success: {save_file_name} outline generated.", "green"))

    # Just want to return the markdown file. We will parse it later.
    return outline_file



