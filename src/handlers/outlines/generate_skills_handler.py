from db.db import DB, Outline
import os
from termcolor import colored
from openai import OpenAI
from ...utils.helpers import get_prompt
from src.utils.files import write_yaml_file



class GenerateSkillsHandler:
    def __init__(self, outline_id: int, llm: OpenAI):
        self.llm_handler = llm
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        self.output_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def handle(self) -> dict:
        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))

        messages = self._build_skills_simple_prompt()

        # Send to ChatGPT
        options = {'yamlExpected': True}
        validated_response = self.llm_handler.send_prompt('skills', messages, options)

        # Save to database
        self.outline.update_properties(DB, {'skills': validated_response['dict']})
        DB.commit()

        write_yaml_file(f"{self.output_path}/skills.yaml", validated_response['yaml'])
        print(colored("Done.", "green"))

        return validated_response


    def _build_skills_simple_prompt(self) -> list[dict]:
        # Build message payload
        system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        user_prompt = get_prompt(self.topic, 'user/outlines/topic-skills', {'topic': self.topic.name})

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
