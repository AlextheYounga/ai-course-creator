import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file
from src.utils.chat_helpers import slugify, get_prompt
import inquirer
import json



class OutlineCreator:
    def __init__(self, topic: str):
        # Initialize OpenAI
        topic_formatted = slugify(topic)
        session_name = f"{topic} Outlines"
        self.ai_handler = OpenAiHandler(session_name)
        self.topic = topic
        self.topic_formatted = topic_formatted
        self.course_material_path = f"src/data/chat/course_material/{topic_formatted}"


    def check_for_existing_outline(self):
        return os.path.exists(f"{self.course_material_path}/master-outline.json")


    def generate_topic_skills(self):
        # Build message payload
        system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        user_prompt = get_prompt('user/topic-skills', [("{topic}", self.topic)])

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {self.topic} skills...", "yellow"))
        response = self.ai_handler.handle_send_json_prompt(messages)
        skills = response['json']

        # Save responses
        save_file_name = f"skills-{self.topic_formatted}"
        self.ai_handler.save_response_json(skills, self.course_material_path, save_file_name)

        return skills


    def generate_series_outline(self, skills: list[dict]):
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        skills_system_prompt = get_prompt('system/skills-prep', [
            ("{topic}", self.topic),
            ("{skills}", json.dumps(skills))
        ])

        user_prompt = get_prompt('user/series-outline', [("{topic}", self.topic)])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            skills_system_prompt,
        ])

        messages = [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {self.topic} series outline...", "yellow"))
        response = self.ai_handler.handle_send_json_prompt(messages)
        outline = response['json']

        # Save responses
        save_file_name = f"series-{self.topic_formatted}"
        self.ai_handler.save_response_json(outline, self.course_material_path, save_file_name)

        return outline


    def generate_chapter_outlines(self, course: dict, series: list[dict]):
        course_name = course['courseName']
        modules = course['modules']

        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        chapters_system_prompt = get_prompt('system/chapters-prep', [
            ("{topic}", self.topic),
            ("{series}", json.dumps(series))
        ])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            chapters_system_prompt,
        ])

        user_prompt = get_prompt('user/chapters-outline', [
            ("{course_name}", course_name),
            ("{modules}", json.dumps(modules))
        ])

        messages = [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Send to ChatGPT and parse JSON
        print(colored(f"Generating {course_name} series chapters...", "yellow"))
        response = self.ai_handler.handle_send_json_prompt(messages)
        chapters = response['json']

        # Save responses
        course_name_formatted = slugify(course_name)
        save_file_name = f"outline-{course_name_formatted}"
        save_path = f"{self.course_material_path}/course-outlines"
        self.ai_handler.save_response_json(chapters, save_path, save_file_name)

        return chapters


    def save_master_outline(self, data):
        save_file = f"{self.course_material_path}/master-outline.json"
        with open(save_file, 'w') as f:
            f.write(json.dumps(data))
            f.close()





def _process_topics(topics: list[str]):
    # Generate series list of courses
    for topic in topics:
        creator = OutlineCreator(topic)

        existing = creator.check_for_existing_outline()
        if (existing):
            print(colored(f"Course outline for {topic} already exists.", "yellow"))
            continue

        skills = creator.generate_topic_skills()
        series = creator.generate_series_outline(skills)

        master_outline = []
        print(colored("\nBegin optimizing course outline...", "yellow"))
        for course in series:
            chapters = creator.generate_chapter_outlines(course, series)
            course_object = {
                "courseName": course['courseName'],
                "chapters": chapters
            }
            master_outline.append(course_object)

        creator.save_master_outline(master_outline)
        print(colored(f"Course outline finalized.", "green"))

    print(colored("All outlines complete.", "green"))


def run_outline_creator():
    try:
        topics = read_json_file("src/data/topics.json")
        topic_choices = ['All'] + topics

        choices = [
            inquirer.List('topic',
                          message="Which topic would you like to generate outlines for?",
                          choices=topic_choices),
        ]

        choice = inquirer.prompt(choices)
        if choice != None:
            answer = choice['topic']

            if answer == 'All':
                _process_topics(topics)
            else:
                _process_topics([answer])

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    run_outline_creator()
