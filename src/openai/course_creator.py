import os
import json
import re
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.files import read_json_file
from src.utils.parse import parse_markdown
from time import sleep

load_dotenv()


class OpenAiHandler:
    def __init__(self):
        # Initialize OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = os.environ.get("MODEL") or 'gpt-3.5-turbo-1106'
        self.payload_path = f"src/data/chat/payloads"
        self.reply_path = f"src/data/chat/replies"

    def parse_markdown_json(self, content: str):
        try:
            soup = parse_markdown(content)
            code_block = soup.find("code").get_text()
            code = re.sub(r"^[^\[]*", "", code_block)
            json_content = json.loads(code)

            return json_content
        except Exception as e:
            print(f"Error parsing markdown: {e}")
            return []


    def send_prompt(self, messages) -> OpenAI:
        print(colored(f"Sending prompt:\n{json.dumps(messages, indent=1)}\n", "cyan"))
        completion = None
        try:
            # Send to ChatGPT
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
        except Exception as e:
            print(f"Error creating course: {e}")
            return None


        sleep(1)  # Give OpenAI a break
        return completion





class CourseCreator:
    def __init__(self):
        # Initialize OpenAI
        self.ai_handler = OpenAiHandler()
        self.prompt_path = f"src/data/prompts"
        self.payload_path = f"src/data/chat/payloads"
        self.reply_path = f"src/data/chat/replies"


    def get_prompt(self, filename, course_name):
        prompt = open(f"{self.prompt_path}/{filename}.md", "r").read()
        return prompt.replace("{course_name}", course_name)

    def generate_series(self, topic):
        # Build message payload
        system_prompt = self.get_prompt('system', topic)
        series_prompt = self.get_prompt('series', topic)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": series_prompt}
        ]

        # Send to ChatGPT
        completion = self.ai_handler.send_prompt(messages)

        # Save responses
        save_file_name = topic.lower().replace(" ", "-") + "-series"
        self.save_responses(completion, topic, save_file_name)

        # Parse outline
        response_content = completion.choices[0].message.content
        series_json = self.ai_handler.parse_markdown_json(response_content)

        return series_json


    def generate_outline(self, course_name):
        # Build message payload
        system_prompt = self.get_prompt('system', course_name)
        outline_prompt = self.get_prompt('outline', course_name)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": outline_prompt}
        ]

        # Send to ChatGPT
        completion = self.ai_handler.send_prompt(messages)

        # Save responses
        formatted_name = course_name.lower().replace(" ", "-")
        save_file_name = formatted_name + "-outline"
        self.payload_path = f"{self.payload_path}/{formatted_name}"
        self.reply_path = f"{self.reply_path}/{formatted_name}"

        self.save_responses(completion, course_name, save_file_name)

        # Parse outline
        response_content = completion.choices[0].message.content
        outline_json = self.ai_handler.parse_markdown_json(response_content)

        return outline_json


    def generate_chapter_material(self, course_name, outline):
        pass

    def check_save_paths(self, path):
        if not (os.path.exists(path)):
            os.mkdir(path)

    def save_responses(self, completion: OpenAI, course_name: str, save_file_name: str) -> None:
        folder_name = course_name.lower().replace(" ", "-")

        # Check paths
        self.check_save_paths(f"{self.payload_path}/{folder_name}")
        self.check_save_paths(f"{self.reply_path}/{folder_name}")

        # Save payload and reply
        payload_file = f"{self.payload_path}/{folder_name}/{save_file_name}.json"
        reply_file = f"{self.reply_path}/{folder_name}/{save_file_name}.md"

        with open(payload_file, 'w') as f:
            f.write(completion.model_dump_json())
            f.close()

        response_content = completion.choices[0].message.content
        with open(reply_file, 'w') as f:
            f.write(response_content)
            f.close()


if __name__ == "__main__":
    topics = read_json_file("src/data/topics.json")

    for topic in topics:
        creator = CourseCreator()
        series = creator.generate_series(topic)

        for course in series:
            outline = creator.generate_outline(course)
            print(outline)
            break

            # creator.generate_chapter_material(course, outline)
