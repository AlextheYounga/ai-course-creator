import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file
from datetime import datetime
import json


class CourseCreator:
    def __init__(self, topic: str):
        # Initialize OpenAI
        topic_formatted = topic.lower().replace(" ", "-")
        self.ai_handler = OpenAiHandler()
        self.topic = topic
        self.topic_formatted = topic_formatted
        self.prompt_path = "src/data/prompts"
        self.payload_path = "src/data/chat/payloads"
        self.creator_path = f"src/data/chat/creator/{topic_formatted}"


    def get_prompt(self, filename, replace: list[tuple]) -> str:
        prompt = open(f"{self.prompt_path}/{filename}.md", "r").read()

        if (replace != None):
            for item in replace:
                prompt = prompt.replace(item[0], item[1])

        return prompt


    def handle_json_prompt(self, messages: list[dict], retry=0):
        completion = self.ai_handler.send_prompt(messages)
        print(colored("Done.", "green"))

        # Parse outline
        response_content = completion.choices[0].message.content
        json_content = self.ai_handler.parse_markdown_json(response_content)

        # If JSON fails to parse, retry
        if (json_content == None):
            if (retry < 3):
                print(colored("Retrying...", "yellow"))
                retry += 1
                self.handle_json_prompt(messages, retry)
            else:
                print(colored("Failed to parse JSON.", "red"))
                return []

        return completion, json_content


    def generate_topic_skills(self):
        # Build message payload
        system_prompt = self.get_prompt('system/general', [("{topic}", self.topic)])
        outline_prompt = self.get_prompt('user/topic-skills', [("{topic}", self.topic)])
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": outline_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {self.topic} skills...", "yellow"))
        completion, skills = self.handle_json_prompt(messages)

        # Save responses
        save_file_name = f"skills-{self.topic_formatted}"
        self._save_responses(completion, self.creator_path, save_file_name)

        return skills

    def generate_series_outline(self, skills: list[dict]):
        # Build message payload
        system_prompt = self.get_prompt('system/skills-prep', [("{topic}", self.topic), ("{skills}", json.dumps(skills))])
        outline_prompt = self.get_prompt('user/series-outline', [("{topic}", self.topic)])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": outline_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {self.topic} series outline...", "yellow"))
        completion, outline = self.handle_json_prompt(messages)

        # Save responses
        save_file_name = f"series-{self.topic_formatted}"
        self._save_responses(completion, self.creator_path, save_file_name)

        return outline


    def _save_responses(self, completion: OpenAI, save_path: str, save_file_name: str) -> None:
        # Check paths
        storage_file = f"{save_path}/{save_file_name}.md"

        self._check_save_paths(self.payload_path)
        self._check_save_paths(save_path)

        # Save payload log
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        payload_file = f"{self.payload_path}/response-{save_file_name}-{timestamp}.json"
        with open(payload_file, 'w') as f:
            f.write(completion.model_dump_json())
            f.close()

        # Save reply
        response_content = completion.choices[0].message.content
        with open(storage_file, 'w') as f:
            f.write(response_content)
            f.close()


    def _check_save_paths(self, path):
        if not (os.path.exists(path)):
            os.mkdir(path)




def run():
    try:
        topics = read_json_file("src/data/topics.json")

        # Generate series list of courses
        for topic in topics:
            creator = CourseCreator(topic)
            skills = creator.generate_topic_skills()
            outline = creator.generate_series_outline(skills)

        #     # Generate course outline
        #     for course in series:
        #         outline = creator.generate_outline(topic, course)

        #         # Generate page material
        #         for item in outline:
        #             # TODO: Add a chapter introduction page
        #             chapter = item['chapterName']
        #             pages = item['pages']

        #             for page in pages:
        #                 creator.generate_page_material(topic, course, page)
        print(colored("Complete.", "green"))

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    run()