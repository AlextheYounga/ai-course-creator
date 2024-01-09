import os
import json
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt
import progressbar
import inquirer


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


    def update_master_outline(self, course_slug: str, chapter_slug: str, page_object: dict):
        page_path = page_object['path']

        self.master_outline['allPaths'].append(page_path)
        self.master_outline['courses'][course_slug]['paths'].append(page_path)
        self.master_outline['courses'][course_slug]['chapters'][chapter_slug]['paths'].append(page_path)
        self.master_outline['courses'][course_slug]['chapters'][chapter_slug]['pages'][page_object['slug']] = page_object

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
        save_file_name = f"challenge-{page_slug}"
        save_path = f"{self.output_path}/content/{course_slug}/{chapter_slug}/{save_file_name}"
        write_markdown_file(save_path, material)

        page_object = {
            "name": 'Practice Skill Challenge',
            "slug": page_slug,
            "path": f"{save_path}.md"
        }

        # Update master outline with new page
        self.update_master_outline(course_slug, chapter_slug, page_object)

        return material


    def create_practice_skill_challenges_for_chapters(self):
        chapters_count = sum([len(data['chapters']) for _, data in self.master_outline['courses'].items()])

        with progressbar.ProgressBar(max_value=chapters_count, prefix='Generating practice skill challenges: ', redirect_stdout=True) as bar:
            for _, course_data in self.master_outline['courses'].items():
                for __, chapter_data in course_data['chapters'].items():
                    bar.increment()
                    self.generate_practice_skill_challenge(course_data, chapter_data)
        return self.master_outline



def main(topics: list[str]):
    # Generate series list of courses
    course_material_path = f"out/course_material"

    for topic in topics:
        print(colored(f"Begin generating {topic} practice skill challenges...", "yellow"))

        # Initialize OpenAI
        session_name = f"{topic} Practice Skill Challenge"
        ai_client = OpenAiHandler(session_name)

        creator = PracticeSkillChallengeCreator(topic, ai_client, course_material_path)
        creator.create_practice_skill_challenges_for_chapters()

    print(colored("Complete.\n", "green"))


def cli_prompt_user():
    try:
        topics = read_json_file("data/topics.json")
        topic_choices = ['All'] + topics

        choices = [
            inquirer.List('topic',
                          message="Which topic would you like to generate practice skill challenges for?",
                          choices=topic_choices),
        ]

        choice = inquirer.prompt(choices)
        if choice != None:
            answer = choice['topic']

            if answer == 'All':
                main(topics)
            else:
                main([answer])

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    cli_prompt_user()
