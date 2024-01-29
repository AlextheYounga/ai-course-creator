import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from db.db import DB, Topic
from .skill_generator import SkillGenerator
from .master_outline_generator import MasterOutlineGenerator
from .outline_processor import OutlineProcessor

load_dotenv()


class OutlineCreator:
    def __init__(
        self,
            topic: str,
            client: OpenAI,
    ):
        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'

        self.topic = self._instantiate_topic(topic)
        self.ai_client = client
        self.output_path = output_directory
        self.outline_file = f"{output_directory}/{self.topic.slug}/master-outline.yaml"


    def create(self):
        existing_outline = os.path.exists(self.outline_file)

        if (existing_outline):
            outline_record = OutlineProcessor.get_or_create_outline_record_from_file(self.topic.id, self.outline_file)
            return outline_record.id

        # Create new outline
        outline = OutlineProcessor.instantiate_new_outline(self.topic.id)
        DB.add(outline)
        DB.commit()

        # Generate Skills
        self.generate_skills(outline.id)

        # Generate Master Outline
        master_outline = self.generate_master_outline(outline.id)

        print(colored("\nOutline generation complete.", "green"))

        course_list = [course['course']['courseName'] for course in master_outline]

        print(colored("\nCourse list: ", "green"))
        print(colored("\n".join(course_list), "green"))

        return outline.id


    def generate_skills(self, outline_id):
        skill_generator = SkillGenerator(outline_id, self.ai_client)
        return skill_generator.generate()


    def generate_master_outline(self, outline_id):
        generator = MasterOutlineGenerator(outline_id, self.ai_client)
        return generator.generate()


    # Private Methods


    def _instantiate_topic(self, topic: str):
        topic_record = DB.query(Topic).filter(Topic.name == topic).first()
        if not topic_record:
            # Save topic to database
            topic_slug = Topic.make_slug(topic)
            topic_record = Topic(name=topic, slug=topic_slug)
            DB.add(topic_record)
            DB.commit()

        return topic_record
