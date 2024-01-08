import os
import json
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt
import progressbar


class PracticeSkillChallengeCreator:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"
        self.outline_path = f"{self.output_path}/master-outline.json"
        self.master_outline = self.get_topic_outline()


    def get_topic_outline(self):
        if not os.path.exists(self.outline_path):
            raise Exception("Course outline not found.")

        try:
            return read_json_file(self.outline_path)
        except Exception as e:
            print(colored(f"Error reading course outline: {e}", "red"))
            return None

    def prepare_datasets(self, course: dict):
        datasets = []
        for path in course['paths']:
            if (os.path.exists(path)):
                page_content = open(path).read()
                datasets.append({"role": "system", "content": page_content})
        return datasets

    def build_skill_challenge_prompt(self, course: dict):
        # Combine multiple system prompts into one
        datasets = self.prepare_datasets(course)

        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        interactives_system_prompt = get_prompt('system/tune-interactives', None)

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
        ])

        user_prompt = get_prompt('user/practice-skill-challenge', None)

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + datasets + user_payload


    def update_master_outline(self, save_path: str, chapter_name: str, page_slug: str):
        page_name = 'Practice Skill Challenge'
        for course_index, course in enumerate(self.master_outline['courses']):
            if course['courseName'] == course['courseName']:
                for cid, c in enumerate(course['chapters']):
                    if c['name'] == chapter_name:
                        page_path = f"{save_path}.md"
                        self.master_outline['allPaths'].append(page_path)
                        self.master_outline['courses'][course_index]['paths'].append(page_path)
                        self.master_outline['courses'][course_index]['chapters'][cid]['paths'].append(page_path)
                        self.master_outline['courses'][course_index]['chapters'][cid]['pages'].append(page_name)
                        self.master_outline['courses'][course_index]['chapters'][cid]['pageSlugs'].append(page_slug)
                        break
                break
        with open(self.outline_path, 'w') as json_file:
            json.dump(self.master_outline, json_file)


    def generate_practice_skill_challenge(self, course: dict, chapter: dict):
        course_slug = course['slug']
        chapter_slug = chapter['slug']
        page_slug = 'practice-skill-challenge'

        messages = self.build_skill_challenge_prompt(course)

        # Send to ChatGPT
        completion = self.ai_client.send_prompt('practice-skill-challenge', messages)
        material = completion.choices[0].message.content

        # Save responses
        save_file_name = f"page-{page_slug}"
        save_path = f"{self.output_path}/content/{course_slug}/{chapter_slug}/{save_file_name}"
        write_markdown_file(save_path, material)

        # Update master outline with new page
        self.update_master_outline(save_path, chapter['name'], page_slug)

        return material

    def create_practice_skill_challenges_for_chapters(self):
        total_count = self.master_outline['totalPages']
        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True) as bar:
            for course in self.master_outline['courses']:
                chapters = course['chapters']
                for chapter in chapters:
                    self.generate_practice_skill_challenge(course, chapter)

        return self.master_outline



def process_pages(topics: list[str]):
    # Generate series list of courses
    course_material_path = f"out/course_material"

    for topic in topics:
        print(colored(f"Begin generating {topic} page material...", "yellow"))

        # Initialize OpenAI
        session_name = f"{topic} Page Material"
        ai_client = OpenAiHandler(session_name)

        creator = PracticeSkillChallengeCreator(topic, ai_client, course_material_path)
        creator.create_pages_from_outline()

    print(colored("Complete.", "green"))
