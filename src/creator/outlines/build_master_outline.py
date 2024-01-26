import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from src.creator.helpers import get_prompt
from src.creator.outlines.outline_processor import OutlineProcessor
from db.db import DB, Outline
import progressbar
import yaml


load_dotenv()


class MasterOutlineBuilder:
    def __init__(self, outline_id: int, client: OpenAI):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        
        self.ai_client = client
        self.outline = DB.get(Outline, outline_id)
        self.topic = self.outline.topic
        self.output_path = f"{output_directory}/{self.topic.slug}"  # master outline sits at topic level
        self.master_outline = []


    def build_optimize_outline_prompt(self, course_name: str, modules: list[dict]) -> list[dict]:
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic.name)])
        chapters_system_prompt = get_prompt('system/tune-draft-outline', [
            ("{topic}", self.topic.name),
            ("{draft_outline}", yaml.dump(self.outline.draft_outline))
        ])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            chapters_system_prompt,
        ])

        user_prompt = get_prompt('user/optimize-course-outline', [
            ("{course_name}", course_name),
            ("{modules}", yaml.dump(modules))
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def generate(self):
        print(colored("\nBegin building master course outline...", "yellow"))

        draft_outline = self.outline.draft_outline

        if draft_outline == None:
            raise Exception("Draft Outline must be generated before generating draft outline.")

        course_count = len(draft_outline)

        with progressbar.ProgressBar(max_value=course_count, prefix='Optimizing: ', redirect_stdout=True) as bar:
            for draft_course in draft_outline:
                # Have ChatGPT optimize this course from the outline.
                self._optimize_course_outline(draft_course)
                bar.increment()

        # Save outlines
        self._save_outlines()

        print(colored("\nCourse outline finalized.", "green"))

        return self.master_outline


    def _save_outlines(self):
        # Save to the database
        outline_hash = OutlineProcessor.hash_outline(self.master_outline)
        existing_outline_record = DB.query(Outline).filter(Outline.hash == outline_hash).first()
        
        if existing_outline_record:
            print(colored("Identical outline already exists. Skipping save to database.", "yellow"))
            self.outline = existing_outline_record
        else:            
            self.outline.master_outline = self.master_outline
            self.outline.hash = outline_hash
            
            DB.add(self.outline)
            DB.commit()

        # Save to YAML file
        os.makedirs(self.output_path, exist_ok=True)
        with open(f"{self.output_path}/master-outline.yaml", 'w') as yaml_file:
            yaml.dump(self.master_outline, yaml_file, sort_keys=False)

        # Save copy to topic series directory
        os.makedirs(f"{self.output_path}/{self.outline.name}", exist_ok=True)
        with open(f"{self.output_path}/{self.outline.name}/outline.yaml", 'w') as yaml_file:
            yaml.dump(self.master_outline, yaml_file, sort_keys=False)


    def _optimize_course_outline(self, draft_course: dict):
        course_name = draft_course['courseName']
        modules = draft_course['modules']

        messages = self.build_optimize_outline_prompt(course_name, modules)

        # Send to ChatGPT
        options = {'yamlExpected': True, 'quiet': True}
        validated_response = self.ai_client.send_prompt('optimize-outline', messages, options)

        # Update master outline
        self._update_master_outline(draft_course, validated_response)

        return validated_response
    

    def _add_challenges_to_chapters(self, chapters):
        chapters_list = []
        # Add Practice Skill Challenges
        for chapter in chapters:
            chapter_object = {
                'name': chapter['chapter'],
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

    def _update_master_outline(self, course: dict, validated_response: dict):
        chapters_list = self._add_challenges_to_chapters(validated_response['dict'])

        course_object = {
            'course': {
                'courseName': course['courseName'],
                'chapters': chapters_list
            }
        }

        self.master_outline.append(course_object)