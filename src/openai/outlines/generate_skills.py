from termcolor import colored
from openai import OpenAI
from src.utils.files import write_json_file
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


    def handle_skills_response(self, content: str):
        yaml_content = content.split("yaml")[1].split("```")[0]
        data = yaml.safe_load(yaml_content)

        return {
            'dict': data,
            'yaml': yaml.dump(yaml_content),
            'plain': yaml_content
        }


    def generate(self) -> dict:
        print(colored(f"Generating {self.topic} skills...", "yellow"))

        save_file_name = f"{self.output_path}/skills-{self.topic_slug}"
        messages = self.build_skills_prompt()

        # Send to ChatGPT
        completion = self.ai_client.send_prompt('skills', messages)
        response_content = completion.choices[0].message.content
        print(colored("Done.", "green"))

        # Parse response
        parsed_response = self.handle_skills_response(response_content)

        write_json_file(save_file_name, parsed_response['dict'])
        return parsed_response
