from termcolor import colored
from openai import OpenAI
from src.utils.files import write_yaml_file
from src.utils.chat_helpers import slugify, get_prompt
import yaml


class OutlineDraft:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        # Initialize OpenAI
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"


    def build_draft_prompt(self, skills: yaml) -> list[dict]:
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        skills_system_prompt = get_prompt('system/tune-skills', [
            ("{topic}", self.topic),
            ("{skills}", yaml.dump(skills))
        ])

        user_prompt = get_prompt('user/draft-outline', [("{topic}", self.topic)])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            skills_system_prompt,
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate(self, skills: dict) -> dict:
        print(colored(f"Generating {self.topic} draft outline...", "yellow"))

        save_file_name = f"{self.output_path}/draft-outline.yaml"
        messages = self.build_draft_prompt(skills['yaml'])

        # Send to ChatGPT 
        options = {'yamlExpected': True}
        validated_response = self.ai_client.send_prompt('draft-outline', messages, options)
        print(colored("Done.", "green"))

        write_yaml_file(save_file_name, validated_response['yaml'])

        return validated_response
