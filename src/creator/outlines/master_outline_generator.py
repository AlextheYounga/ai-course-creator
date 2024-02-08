import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from db.db import DB, Outline
import yaml


load_dotenv()


class MasterOutlineGenerator:
    def __init__(self, outline_id: int, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.ai_client = client
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}"  # master outline sits at topic level
        self.series_path = f"{output_directory}/{self.topic.slug}/{self.outline.name}"


    def build_master_outline_prompt(self) -> list[dict]:
        # Build message payload
        skills = self.outline.skills
        if skills == None:
            raise Exception("Skills must be generated before generating master outline.")

        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        skills_system_prompt = get_prompt('system/outlines/tune-skills', [
            ("{topic}", self.topic.name),
            ("{skills}", yaml.dump(skills))
        ])

        user_prompt = get_prompt('user/outlines/master-outline', [("{topic}", self.topic.name)])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            skills_system_prompt,
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def construct_full_master_outline_from_response(self, outline_response: dict) -> dict:
        master_outline = []

        for course in outline_response:
            chapters_list = self._add_challenges_to_chapters(course)

            master_outline.append({
                'course': {
                    'courseName': course['courseName'],
                    'chapters': chapters_list
                }
            })

        return master_outline


    def generate(self) -> dict:
        print(colored(f"Generating {self.topic.name} master outline...", "yellow"))

        messages = self.build_master_outline_prompt()

        # Send to ChatGPT
        options = {'yamlExpected': True}
        validated_response = self.ai_client.send_prompt('master-outline', messages, options)

        master_outline = self.construct_full_master_outline_from_response(validated_response['dict'])

        # Save to database
        self.outline.master_outline = master_outline
        outline_hash = Outline.hash_outline(master_outline)

        # Check for existing outline based on hash
        existing_outline = DB.query(Outline).filter(Outline.hash == outline_hash).first()
        if existing_outline:
            print(colored("Identical outline found. Using existing outline.", "yellow"))
            self.outline = existing_outline
        else:
            DB.add(self.outline)
            DB.commit()

        # Save to YAML file
        os.makedirs(self.output_path, exist_ok=True)
        with open(f"{self.output_path}/master-outline.yaml", 'w') as yaml_file:
            yaml.dump(master_outline, yaml_file, sort_keys=False)

        # Save copy to topic series directory
        os.makedirs(f"{self.series_path}", exist_ok=True)
        with open(f"{self.series_path}/outline.yaml", 'w') as yaml_file:
            yaml.dump(master_outline, yaml_file, sort_keys=False)

        print(colored("Done.", "green"))

        return self.outline


    # Private Methods


    def _add_challenges_to_chapters(self, course: dict) -> list:
        chapters_list = []
        # Add Practice Skill Challenges
        for chapter in course['chapters']:
            chapter_object = {
                'name': chapter['name'],
                'pages': [
                    *chapter['pages'],
                    'Practice Skill Challenge'
                ]
            }
            chapters_list.append(chapter_object)

        # Add Final Skill Challenge
        chapters_list.append({
            'name': 'Final Skill Challenge',
            'pages': [f"Final Skill Challenge Page {i}" for i in range(1, 5)]
        })

        return chapters_list
