from db.db import DB, Topic, Outline
from termcolor import colored
from src.handlers.start_new_thread_handler import StartNewThreadHandler
from src.handlers.outlines import *


class GenerateOutline:
    def __init__(self, topic_id: int):
        self.topic = DB.get(Topic, topic_id)
        self.thread = None

    def run(self):
        self.thread = StartNewThreadHandler('GenerateOutline').handle()

        outline = InstantiateOutlineHandler(self.thread.id, self.topic.id).handle()

        outline = self._generate_skills(outline)

        outline = self._generate_outline_chunks(outline)

        outline = CompileOutlineChunksToMasterOutlineHandler(outline.id).handle()

        return outline


    def _generate_skills(self, outline: Outline):
        skills_prompt = CreateGenerateSkillsPromptHandler(self.thread.id, outline.id).handle()
        skills_response = SendGenerateSkillsPromptHandler(self.thread.id, outline.id, skills_prompt.id).handle()
        outline = ProcessGenerateSkillsResponseHandler(self.thread.id, outline.id, skills_response.id).handle()

        return outline


    def _generate_outline_chunks(self, outline: Outline):
        chunk_prompt_ids = CreateGenerateOutlineChunksPromptHandler(self.thread.id, outline.id).handle()
        chunks_response_ids = SendGenerateOutlineChunksPromptsHandler(self.thread.id, outline.id, chunk_prompt_ids).handle()
        outline = ProcessGenerateOutlineChunksResponsesHandler(self.thread.id, outline.id, chunks_response_ids).handle()

        return outline
