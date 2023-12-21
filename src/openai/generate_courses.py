import os
import json
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.files import read_json_file
from src.openai.generate_outline import generate_course_outline
from src.openai.parse_course_outline import parse_course_outline
from time import sleep

load_dotenv()

MODEL = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
PAYLOAD_PATH = f"src/data/chat/payloads"
REPLY_PATH = f"src/data/chat/replies"
COURSES_PATH = "src/data/courses.json"
SYSTEM_CONTEXT_TEMPLATE = open("src/data/prompts/post-outline-system.md", "r").read()



def create_courses():
    courses = read_json_file(COURSES_PATH)

    for course in courses:
        folder_name = course.lower().replace(" ", "-")
        save_file_name = course.lower().replace(" ", "-")
        _check_output_paths(save_file_name)

        outline_file = generate_course_outline(course)
        course_outline_content = open(outline_file, "r").read()
        outline_structure = parse_course_outline(course_outline_content)
        
        # Initialize OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        i = 0
        for topic in outline_structure:
            i += 1

            # Build message payload
            system_prompt = SYSTEM_CONTEXT_TEMPLATE.format(course_name=course)
            user_prompt = _build_dynamic_prompt_from_outline(topic)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            print(colored(f"Sending prompt:\n{json.dumps(messages, indent=1)}\n", "cyan"))
            completion = None
            try:
                # Send to ChatGPT
                completion = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                )
            except Exception as e:
                print(f"Error creating course: {e}")
                break

            _write_output_files(completion, folder_name, save_file_name, i)

            print(colored(f"Success: {save_file_name} {i} course content saved.", "green"))
            sleep(1)
            


def _check_output_paths(folder_name: str) -> None:
    if not (os.path.exists(f"{PAYLOAD_PATH}/{folder_name}")):
        os.mkdir(f"{PAYLOAD_PATH}/{folder_name}")
    if not (os.path.exists(f"{REPLY_PATH}/{folder_name}")):
        os.mkdir(f"{REPLY_PATH}/{folder_name}")



def _build_dynamic_prompt_from_outline(topic: dict) -> str:
    header = topic["header"]
    children = topic["children"]
    formatted_children = [f"- {child}" for child in children]
    children_str = "\n".join(formatted_children)

    prompt = f"""
    Please create content for a new course page. The page should be titled "{header}" and should include the following content:
    {children_str}
    """

    return prompt



def _write_output_files(completion, folder_name: str, save_file_name: str, iteration: int) -> None:
    payload_file = f"{PAYLOAD_PATH}/{folder_name}/{save_file_name}-{iteration}.json"
    reply_file = f"{REPLY_PATH}/{folder_name}/{save_file_name}-{iteration}.md"

    with open(payload_file, 'w') as f:
        f.write(completion.model_dump_json())
        f.close()

    with open(reply_file, 'w') as f:
        f.write(completion.choices[0].message.content)
        f.close()
