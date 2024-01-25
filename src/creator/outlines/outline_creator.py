import os
from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from db.db import db_client, Topic, Outline
from src.utils.strings import slugify
from .skill_generator import SkillGenerator
from .draft_outline import DraftOutline
from .build_master_outline import MasterOutlineBuilder
from .outline_processor import OutlineProcessor

load_dotenv()
DB = db_client()


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
        outline = self._instantiate_outline()

        # Generate Skills
        self.generate_skills(outline.id)

        # Generate Draft Outline
        self.generate_draft_outline(outline.id)

        # Finalize Outline
        master_outline = self.generate_master_outline(outline.id)

        print(colored("\nOutline generation complete.", "green"))

        course_list = [course['course']['courseName'] for course in master_outline]

        print(colored("\nCourse list: ", "green"))
        print(colored("\n".join(course_list), "green"))

        return outline.id


    def generate_skills(self, outline_id):
        skill_generator = SkillGenerator(outline_id, self.ai_client)
        return skill_generator.generate()


    def generate_draft_outline(self, outline_id):
        draft = DraftOutline(outline_id, self.ai_client)
        return draft.generate()


    def generate_master_outline(self, outline_id):
        builder = MasterOutlineBuilder(outline_id, self.ai_client)
        return builder.generate()


    def _instantiate_topic(self, topic: str):
        topic_record = DB.query(Topic).filter(Topic.name == topic).first()
        if not topic_record:
            # Save topic to database
            topic_record = Topic(name=topic, slug=slugify(topic),)
            DB.add(topic_record)
            DB.commit()

        return topic_record


    def _instantiate_outline(self):
        outline = Outline.instantiate(self.topic)
        DB.add(outline)
        DB.commit()

        return outline
