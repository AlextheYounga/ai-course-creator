import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from src.utils.files import write_yaml_file
from db.db import db_client, Outline
import yaml


load_dotenv()
DB = db_client()


class DraftOutline:
    def __init__(self, outline_id: int, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        
        self.ai_client = client
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def build_draft_prompt(self) -> list[dict]:
        # Build message payload
        skills = self.outline.skills
        if skills == None:
            raise Exception("Skills must be generated before generating draft outline.")

        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        skills_system_prompt = get_prompt('system/tune-skills', [
            ("{topic}", self.topic.name),
            ("{skills}", yaml.dump(skills))
        ])

        user_prompt = get_prompt('user/draft-outline', [("{topic}", self.topic.name)])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            skills_system_prompt,
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate(self) -> dict:
        print(colored(f"Generating {self.topic.name} draft outline...", "yellow"))

        messages = self.build_draft_prompt()

        # Send to ChatGPT
        options = {'yamlExpected': True}
        validated_response = self.ai_client.send_prompt('draft-outline', messages, options)

        # Save to database
        self.outline.draft_outline = validated_response['dict']
        DB.add(self.outline)
        DB.commit()

        write_yaml_file(f"{self.output_path}/draft-outline.yaml", validated_response['yaml'])
        print(colored("Done.", "green"))

        return validated_response
