import os
from termcolor import colored
from openai import OpenAI
from .openai_handler import OpenAiHandler
from src.utils.files import read_json_file, write_json_file
from src.utils.chat_helpers import slugify, get_prompt
from bs4 import BeautifulSoup
import markdown
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


    def check_for_existing_outlines(self):
        existing = os.path.exists(f"{self.course_material_path}/master-outline.json")
        if (existing):
            print(colored(f"Course outline for {self.topic} already exists.", "yellow"))
            return False
        return True


    def build_skills_prompt(self):
        # Build message payload
        system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        user_prompt = get_prompt('user/topic-skills', [("{topic}", self.topic)])

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def build_series_prompt(self, skills: list[dict]):
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        skills_system_prompt = get_prompt('system/tune-skills', [
            ("{topic}", self.topic),
            ("{skills}", json.dumps(skills))
        ])

        user_prompt = get_prompt('user/series-outline', [("{topic}", self.topic)])

        combined_system_prompt = "\n".join([
            general_system_prompt,
            skills_system_prompt,
        ])

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def build_chapter_outlines_prompt(self, course_name: str, series: list[dict], modules: list[dict]):
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        chapters_system_prompt = get_prompt('system/tune-chapters', [
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

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def handle_topics_response(self, content: str):
        soup = BeautifulSoup(content, 'html.parser')
        data_block = soup.find("div", {'id': "data"})
        html_string = markdown.markdown(data_block.get_text())
        data_soup = BeautifulSoup(html_string, 'html.parser')

        json_list = []
        ol = data_soup.find("ol")
        for item in ol.find_all("li"):
            if item.findChildren("li") == []: continue

            header = item.find("p") or item.find("strong")
            children_ul = item.find("ul")
            children = [li.get_text() for li in children_ul.find_all("li")]
            outline_item = {"header": header.get_text(), "children": children}
            json_list.append(outline_item)

        return {
            'json': json_list,
            'plain': data_block.get_text()
        }


    def handle_series_response(self, content: str):
        soup = BeautifulSoup(content, 'html.parser')
        data_block = soup.find("div", {'id': "data"})

        with open("test/fixtures/soups/series.html", "w") as file:
            file.write(str(data_block))

        json_list = []
        courses = data_block.find_all("div", {"class": "course"})
        for course in courses:
            course_name = course.find("h3").get_text()
            modules = course.find_all("section", {"class": "module"})
            course_object = {"courseName": course_name, "modules": []}

            for module in modules:
                module_name = module.find("strong").get_text()
                children = [li.get_text() for li in module.find_all("li")]
                module_object = {"name": module_name, "skills": children}
                course_object["modules"].append(module_object)

            json_list.append(course_object)

        return {
            'json': json_list,
            'plain': data_block.get_text()
        }


    def handle_chapters_response(self):
        pass


    def generate_topic_skills(self):
        print(colored(f"Generating {self.topic} skills...", "yellow"))
        save_file_name = f"{self.course_material_path}/skills-{self.topic_formatted}"
        messages = self.build_skills_prompt()
        completion = self.ai_handler.send_prompt(messages)
        json_content = self.handle_topics_response(completion)
        write_json_file(save_file_name, json_content)
        return json_content


    def generate_series_outline(self):
        print(colored(f"Generating {self.topic} series outline...", "yellow"))
        save_file_name = f"{self.course_material_path}/series-{self.topic_formatted}"
        messages = self.build_series_prompt()
        completion = self.ai_handler.send_prompt(messages)
        json_content = self.handle_series_response(completion)
        write_json_file(save_file_name, json_content)
        return json_content


    def generate_chapter_outlines(self, course: dict, series: list[dict]):
        print(colored(f"Generating {course_name} series chapters...", "yellow"))
        course_name = course['courseName']
        modules = course['modules']

        course_name_formatted = slugify(course_name)
        save_file_name = f"outline-{course_name_formatted}"
        save_path = f"{self.course_material_path}/course-outlines"
        save_file_path = f"{save_path}/{save_file_name}.json"

        messages = self.build_chapter_outlines_prompt(course_name, series, modules)
        completion = self.ai_handler.send_prompt(messages)
        json_content = self.handle_chapters_response(completion)

        write_json_file(save_file_path, json_content)
        return json_content


    def generate_master_outline(self, series: list[dict]):
        print(colored("\nBegin building master course outline...", "yellow"))
        master_outline = []
        for course in series:
            chapters = self.generate_chapter_outlines(course, series)
            course_object = {
                "courseName": course['courseName'],
                "chapters": chapters
            }
            master_outline.append(course_object)
        write_json_file(f"{self.course_material_path}/master-outline.json", master_outline)
        print(colored(f"Course outline finalized.", "green"))
        return master_outline


def _process_topics(topics: list[str]):
    # Generate series list of courses
    for topic in topics:
        creator = OutlineCreator(topic)
        existing = creator.check_for_existing_outlines()

        if not existing:
            skills = creator.generate_topic_skills()
            series = creator.generate_series_outline(skills)
            master_outline = creator.generate_master_outline(series)

            course_list = [c['courseName'] for c in master_outline]
            print(colored("Course list: ", "green"))
            print(colored("\n".join(course_list), "green"))

    print(colored("\nAll outlines complete.", "green"))


def create_outlines():
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
    create_outlines()


# with open("test/fixtures/soups/series.html", "w") as file:
    #     file.write(str(data_block))
