from termcolor import colored
from openai import OpenAI
from src.utils.files import write_yaml_file
from src.utils.chat_helpers import slugify, get_prompt
import yaml


class SkillGenerator:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        # Initialize OpenAI
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"


    def build_skills_prompt(self) -> list[dict]:
        # Build message payload
        system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        user_prompt = get_prompt('user/topic-skills', [("{topic}", self.topic)])

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate(self) -> dict:
        print(colored(f"Generating {self.topic} skills...", "yellow"))

        save_file_name = f"{self.output_path}/skills.yaml"
        messages = self.build_skills_prompt()

        # Send to ChatGPT
        options = {'yamlExpected': True}
        validated_response = self.ai_client.send_prompt('skills', messages, options)
        print(colored("Done.", "green"))

        # Parse yaml
        yaml_content = validated_response['yaml']

        write_yaml_file(save_file_name, yaml_content)

        return validated_response
