from termcolor import colored
from openai import OpenAI
from src.utils.files import write_yaml_file, write_json_file
from src.utils.chat_helpers import slugify, get_prompt, copy_master_outline_to_yaml
import progressbar
import yaml


class MasterOutlineBuilder:
    def __init__(self, topic: str, client: OpenAI, output_path: str):
        # Initialize OpenAI
        topic_slug = slugify(topic)
        self.ai_client = client
        self.topic = topic
        self.topic_slug = topic_slug
        self.output_path = f"{output_path}/{topic_slug}"
        self.master_outline = {
            'topic': self.topic,
            'totalPages': 0,
            'courses': {}
        }


    def build_optimize_outline_prompt(self, course_name: str, draft_outline: list[dict], modules: list[dict]) -> list[dict]:
        # Build message payload
        general_system_prompt = get_prompt('system/general', [("{topic}", self.topic)])
        chapters_system_prompt = get_prompt('system/tune-draft-outline', [
            ("{topic}", self.topic),
            ("{draft_outline}", yaml.dump(draft_outline))
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


    def update_master_outline(self, course: dict, course_slug: str, parsed_response: dict):
        # Building course
        course_object = {
            "courseName": course['courseName'],
            'slug': course_slug,
            "chapters": {},
            "pageCount": 0,
            'paths': []  # Will update this later in page material creator
        }

        for chapter in parsed_response['dict']:
            # Building chapter object
            chapter_name = chapter.get('chapter', False) or chapter['name']
            chapter_slug = slugify(chapter_name)
            chapter_page_count = len(chapter['pages'])
            course_object['pageCount'] += chapter_page_count

            chapter_object = {
                'name': chapter_name,
                'slug': chapter_slug,
                'pageCount': chapter_page_count,
                'pages': {},
                'paths': [],  # Will update this later in page material creator
            }

            # Building page object
            for page in chapter['pages']:
                if isinstance(page, str):
                    page_slug = slugify(page)
                    page_object = {
                        'name': page,
                        'slug': page_slug,
                    }
                    chapter_object['pages'][page_slug] = page_object
            course_object['chapters'][chapter_slug] = chapter_object

        self.master_outline['totalPages'] += course_object['pageCount']
        self.master_outline['courses'][course_slug] = course_object


    def optimize_course_outline(self, course: dict, draft_outline: dict):
        course_name = course['courseName']
        modules = course['modules']

        course_slug = slugify(course_name)
        save_file_name = f"outline-{course_slug}"
        save_path = f"{self.output_path}/course-outlines"
        save_file_path = f"{save_path}/{save_file_name}.yaml"

        messages = self.build_optimize_outline_prompt(course_name, draft_outline['yaml'], modules)

        # Send to ChatGPT
        options = {'yamlExpected': True, 'quiet': True}
        validated_response = self.ai_client.send_prompt('optimize-outline', messages, options)

        # Parse yaml
        yaml_content = validated_response['yaml']
        validated_response['dict'] = yaml.safe_load(yaml_content)

        # Update master outline
        self.update_master_outline(course, course_slug, validated_response)

        # Save outline response
        write_yaml_file(save_file_path, yaml_content)

        return validated_response


    def generate(self, draft_outline: dict):
        print(colored("\nBegin building master course outline...", "yellow"))

        course_count = len(draft_outline['dict'])
        with progressbar.ProgressBar(max_value=course_count, prefix='Optimizing: ', redirect_stdout=True) as bar:
            for course in draft_outline['dict']:
                # Have ChatGPT optimize this course from the outline.
                self.optimize_course_outline(course, draft_outline)
                bar.increment()


        write_json_file(f"{self.output_path}/master-outline.json", self.master_outline)
        copy_master_outline_to_yaml(f"{self.output_path}/master-outline.yaml", self.master_outline)
        print(colored(f"Course outline finalized.", "green"))

        return self.master_outline
