import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from db.db import DB, Topic, Outline
from .skill_generator import SkillGenerator
from .master_outline_generator import MasterOutlineGenerator

load_dotenv()


class OutlineCreator:
    def __init__(
        self,
            topic: str,
            client: OpenAI,
    ):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.topic = Topic.first_or_create(DB, topic)
        self.ai_client = client
        self.output_path = output_directory
        self.outline_file = f"{output_directory}/{self.topic.slug}/master-outline.yaml"


    def create(self):
        # Create new outline
        outline = Outline.instantiate(DB, self.topic.id)
        DB.add(outline)
        DB.commit()

        # Generate Skills
        self.generate_skills(outline.id)

        # Generate Master Outline
        master_outline = self.generate_master_outline(outline.id)

        # Process Outline
        print(colored("\nProcessing Outline...", "yellow"))
        Outline.process_outline(DB, self.topic.id, self.outline_file)
        print(colored("Outline generation complete.\n", "green"))

        # Print course
        course_list = [f" - {course['course']['courseName']}" for course in master_outline]
        print(colored("\nCourse list: ", "green"))
        print(colored("\n".join(course_list) + "\n", "green"))



        return outline.id


    def generate_skills(self, outline_id):
        skill_generator = SkillGenerator(outline_id, self.ai_client)
        return skill_generator.generate()


    def generate_master_outline(self, outline_id):
        generator = MasterOutlineGenerator(outline_id, self.ai_client)
        return generator.generate()
