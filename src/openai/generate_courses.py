import os
import json
from termcolor import colored
from src.utils.files import read_json_file
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gpt-3.5-turbo-1106"
PAYLOAD_PATH = f"src/data/chat/payloads"
REPLY_PATH = f"src/data/chat/replies"
CONTEXT_PATH = f"src/data/chat/context"

INITIAL_PROMPT = open("src/data/prompts/start.md", "r").read()
SYSTEM_CONTEXT_PROMPT = open("src/data/prompts/system.md", "r").read()


def main():
    courses = read_json_file('src/data/courses.json')

    for course in courses:
        folder_name = course.lower().replace(" ", "_")
        save_file_name = course.lower().replace(" ", "_")

        _check_output_paths(save_file_name)

        # Initialize OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Build initial message payload
        messages = [
            {"role": "system", "content": SYSTEM_CONTEXT_PROMPT},
            {"role": "user", "content": INITIAL_PROMPT}
        ]

        for iteration in range(1):
            if (iteration > 0):
                continue_prompt = open(
                    "src/data/prompts/continue.md", "r").read()
                messages.append({"role": "user", "content": continue_prompt})

            try:
                # Send to ChatGPT
                completion = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                )

                latest_message = json.loads(completion.choices[0].message.model_dump_json())
                messages.append(latest_message)

                _write_output_files(
                    completion,
                    messages,
                    folder_name,
                    save_file_name,
                    iteration
                )

                print(
                    colored(f"Success: {save_file_name} reply received.", "green"))
            except Exception as e:
                print(f"Error: {e}")


def _write_output_files(completion, messages, folder_name, save_file_name, iteration):
    payload_file = f"{PAYLOAD_PATH}/{folder_name}/{save_file_name}-{iteration}.json"
    reply_file = f"{REPLY_PATH}/{folder_name}/{save_file_name}-{iteration}.md"
    context_file = f"{CONTEXT_PATH}/{save_file_name}.json"

    with open(context_file, 'w') as f:
        f.write(json.dumps(messages))
        f.close()

    with open(payload_file, 'w') as f:
        f.write(completion.model_dump_json())
        f.close()

    with open(reply_file, 'w') as f:
        f.write(completion.choices[0].message.content)
        f.close()


def _check_output_paths(folder_name):
    if not (os.path.exists(f"{PAYLOAD_PATH}/{folder_name}")):
        os.mkdir(f"{PAYLOAD_PATH}/{folder_name}")
    if not (os.path.exists(f"{REPLY_PATH}/{folder_name}")):
        os.mkdir(f"{REPLY_PATH}/{folder_name}")
