import os
import json
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_markdown_file
from src.utils.chat_helpers import slugify, get_prompt, copy_master_outline_to_yaml
import progressbar
import inquirer


class FinalSkillChallengeCreator:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"
        self.outline_path = f"{self.output_path}/master-outline.json"
        self.master_outline = self.get_master_outline()


    def get_master_outline(self):
        if not os.path.exists(self.outline_path):
            raise Exception("Course outline not found.")

        try:
            return read_json_file(self.outline_path)
        except Exception as e:
            print(colored(f"Error reading course outline: {e}", "red"))
            return None


    def prepare_course_content_prompt(self, course: dict):
        # Combine all page content into a single string
        course_pages_content = "The following is all the content from this course:\n\n"
        for path in course['paths']:
            if (os.path.exists(path)):
                page_content = open(path).read()
                course_pages_content += f"{page_content}\n\n"
        return course_pages_content


    def build_skill_challenge_prompt(self, course: dict):
        # Combine all page content into a single string
        all_pages_content = self.prepare_course_content_prompt(course)

        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        interactives_system_prompt = get_prompt('system/tune-interactives', None)

        combined_system_prompt = "\n".join([
            general_system_prompt,
            interactives_system_prompt,
            all_pages_content
        ])

        user_prompt = get_prompt('user/final-skill-challenge', None)

        # Build message payload
        system_payload = [{"role": "system", "content": combined_system_prompt}]
        user_payload = [{"role": "user", "content": user_prompt}]

        return system_payload + user_payload


    def update_master_outline(self, course_slug: str, save_file_path: str):
        page_path = f"{save_file_path}.md"
        self.master_outline['allPaths'].append(page_path)
        self.master_outline['courses'][course_slug]['paths'].append(page_path)
        self.master_outline['courses'][course_slug]['chapters']['final-skill-challenge'] = {
            "name": "Final Skill Challenge",
            "slug": "final-skill-challenge",
            "paths": [page_path],
            "pages": {
                'page-final-skill-challenge': {
                    "name": 'Final Skill Challenge',
                    "slug": 'page-final-skill-challenge',
                    "path": page_path
                }

            }
        }

        with open(self.outline_path, 'w') as json_file:
            json.dump(self.master_outline, json_file)


    def generate_final_skill_challenge(self, course: dict):
        course_slug = course['slug']

        messages = self.build_skill_challenge_prompt(course)

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('final-skill-challenge', messages, options={})
        material = validated_response['content']

        # Save responses
        save_file_name = "final-skill-challenge"
        save_path = f"{self.output_path}/content/{course_slug}/final-skill-challenge/{save_file_name}"
        write_markdown_file(save_path, material)

        # Update master outline with new page
        self.update_master_outline(course_slug, save_path)

        return material


    def create_final_skill_challenges_for_courses(self):
        courses_count = len([slug for slug in self.master_outline['courses']])

        with progressbar.ProgressBar(max_value=courses_count, prefix='Generating final skill challenges: ', redirect_stdout=True) as bar:
            for course_data in self.master_outline['courses'].values():
                self.generate_final_skill_challenge(course_data)
                bar.increment()

        copy_master_outline_to_yaml(self.outline_path, self.master_outline)
        return self.master_outline



def main(topics: list[str]):
    # Generate series list of courses
    course_material_path = f"out/course_material"

    for topic in topics:
        print(colored(f"Begin generating {topic} final skill challenges...", "yellow"))

        # Initialize OpenAI
        session_name = f"{topic} Final Skill Challenge"
        ai_client = OpenAiHandler(session_name)

        creator = FinalSkillChallengeCreator(topic, ai_client, course_material_path)
        creator.create_final_skill_challenges_for_courses()

    print(colored("Complete.\n", "green"))


def cli_prompt_user():
    try:
        topics = read_json_file("data/topics.json")
        topic_choices = ['All'] + topics

        choices = [
            inquirer.List('topic',
                          message="Which topic would you like to generate final skill challenges for?",
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
