from db.db import DB, Page, Outline, OutlineEntity, Prompt, Response
from ...llm.get_llm_client import get_llm_client
from .create_practice_skill_challenge_prompt_handler import CreatePracticeSkillChallengePromptHandler
from openai.types.completion import Completion
from termcolor import colored



class SendGeneratePracticeChallengePromptToLLMHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.page = DB.get(Page, data['pageId'])
        self.topic = self.outline.topic



    def handle(self):
        # Check if chapter is incomplete
        if self._check_chapter_incomplete(self.page):
            print(colored("Chapter is incomplete, skipping LLM prompt generation", "yellow"))
            return None

        # Build prompt
        prompt_handler = CreatePracticeSkillChallengePromptHandler(self.thread_id, self.outline, self.page)
        prompt = prompt_handler.handle()
        messages = prompt.payload

        # Send to ChatGPT
        llm_client = get_llm_client()
        completion = llm_client.send_prompt('practice-skill-challenge', messages)

        if completion == None:
            raise Exception("LLM completion failed. There is likely more output in the logs.")

        response = self._save_response_payload_to_db(prompt, completion)

        return response


    def _save_response_payload_to_db(self, prompt: Prompt, completion: Completion):
        properties = {
            'params': prompt.properties['params'],
        }

        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=prompt.id,
            role=completion.choices[0].message.role,
            payload=completion.model_dump_json(),
            model=completion.model,
            prompt_tokens=completion.usage.prompt_tokens,
            completion_tokens=completion.usage.completion_tokens,
            total_tokens=completion.usage.total_tokens,
            content=completion.choices[0].message.content,
            properties=properties
        )

        DB.add(response)
        DB.commit()

        return response

    def _check_chapter_incomplete(self, page: Page):
        chapter_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.course_id == page.course_id,
            Page.chapter_id == page.chapter_id,
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        return True in [page.content == None for page in chapter_pages]
