from termcolor import colored
from openai import OpenAI
from db.db import DB, Topic, Outline
from src.handlers.outlines.generate_skills_handler import GenerateSkillsHandler
from src.handlers.outlines.generate_outline_chunks_handler import GenerateOutlineChunksHandler
from src.handlers.outlines.compile_master_outline_handler import CompileMasterOutlineHandler


class GenerateOutline:
    def __init__(self, topic_id: int, llm: OpenAI):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm


    def run(self):
        outline = self._instantiate_outline()

        self._generate_skills(outline.id)

        outline = self._generate_outline_chunks(outline.id)

        outline = self._compile_master_outline(outline.id)

        self._process_outline(outline)

        # Print course
        course_list = [f" - {course['course']['courseName']}" for course in outline.master_outline]
        print(colored("\nCourse list: ", "green"))
        print(colored("\n".join(course_list) + "\n", "green"))

        return outline.id

    def _instantiate_outline(self):
        # Create new outline
        outline = Outline.instantiate(DB, self.topic.id)
        DB.add(outline)
        DB.commit()

        return outline

    def _generate_skills(self, outline_id):
        handler = GenerateSkillsHandler(outline_id, self.llm_handler)
        return handler.handle()


    def _generate_outline_chunks(self, outline_id):
        handler = GenerateOutlineChunksHandler(outline_id, self.llm_handler)
        return handler.handle()


    def _compile_master_outline(self, outline_id):
        handler = CompileMasterOutlineHandler(outline_id)
        return handler.handle()


    def _process_outline(self, outline: Outline):
        print(colored("\nProcessing Outline...", "yellow"))
        Outline.create_outline_entities(DB, outline.id)
        print(colored("Outline generation complete.\n", "green"))
