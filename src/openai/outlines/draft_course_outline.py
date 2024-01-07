from termcolor import colored
from openai import OpenAI
from src.utils.files import write_json_file, write_yaml_file
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


    def handle_outline_draft_response(self, content: str):
        yaml_content = content.split("yaml")[1].split("```")[0]
        data = yaml.safe_load(yaml_content)

        return {
            'dict': data,
            'yaml': yaml_content
        }


    def generate(self, skills: dict) -> dict:
        print(colored(f"Generating {self.topic} draft outline...", "yellow"))

        save_file_name = f"{self.output_path}/draft-outline-{self.topic_slug}.yaml"
        messages = self.build_draft_prompt(skills['yaml'])

        # Send to ChatGPT
        completion = self.ai_client.send_prompt('draft-outline', messages)
        response_content = completion.choices[0].message.content
        print(colored("Done.", "green"))

        # Parse response
        parsed_response = self.handle_outline_draft_response(response_content)

        write_yaml_file(save_file_name, parsed_response['yaml'])
        return parsed_response
