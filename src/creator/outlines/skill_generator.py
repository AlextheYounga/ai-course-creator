import os
from termcolor import colored
from openai import OpenAI
from dotenv import load_dotenv
from db.db import DB, Outline
from src.creator.helpers import get_prompt
from src.utils.files import write_yaml_file


load_dotenv()


class SkillGenerator:
    def __init__(self, outline_id: int, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.ai_client = client
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def build_skills_prompt(self) -> list[dict]:
        # Build message payload
        system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        user_prompt = get_prompt('user/topic-skills', [("{topic}", self.topic.name)])

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate(self) -> dict:
        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))

        messages = self.build_skills_prompt()

        # Send to ChatGPT
        options = {'yamlExpected': True}
        validated_response = self.ai_client.send_prompt('skills', messages, options)

        # Save to database
        self.outline.skills = validated_response['dict']
        DB.add(self.outline)
        DB.commit()

        write_yaml_file(f"{self.output_path}/skills.yaml", validated_response['yaml'])
        print(colored("Done.", "green"))

        return validated_response
