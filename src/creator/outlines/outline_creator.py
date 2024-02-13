from termcolor import colored
from dotenv import load_dotenv
from openai import OpenAI
from db.db import DB, Topic, Outline
from .skill_generator import SkillGenerator
from .outline_chunk_generator import OutlineChunkGenerator
from .master_outline_compiler import MasterOutlineCompiler

load_dotenv()


class OutlineCreator:
    def __init__(
        self,
            topic_id: int,
            client: OpenAI,
    ):
        self.topic = DB.get(Topic, topic_id)
        self.ai_client = client


    def create(self):
        # Create new outline
        outline = Outline.instantiate(DB, self.topic.id)
        DB.add(outline)
        DB.commit()

        # Generate Skills
        self.generate_skills(outline.id)

        # Generate Outline Chunks
        outline = self.generate_outline_chunks(outline.id)

        # Generate Master Outline
        outline = self.compile_master_outline(outline.id)

        # Process Outline
        print(colored("\nProcessing Outline...", "yellow"))
        Outline.process_outline(DB, self.topic.id, outline.file_path)
        print(colored("Outline generation complete.\n", "green"))

        # Print course
        course_list = [f" - {course['course']['courseName']}" for course in outline.master_outline]
        print(colored("\nCourse list: ", "green"))
        print(colored("\n".join(course_list) + "\n", "green"))

        return outline.id


    def generate_skills(self, outline_id):
        skill_generator = SkillGenerator(outline_id, self.ai_client)
        return skill_generator.generate()


    def generate_outline_chunks(self, outline_id):
        generator = OutlineChunkGenerator(outline_id, self.ai_client)
        return generator.generate_chunks()


    def compile_master_outline(self, outline_id):
        compiler = MasterOutlineCompiler(outline_id)
        return compiler.compile()
