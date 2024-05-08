from termcolor import colored
import json
from openai.types.completion import Completion
from db.db import DB, Topic, Prompt, Response
from src.events.events import GenerateSkillsResponseReceivedFromOpenAI
from src.utils.llm.get_llm_client import get_llm_client



class SendGenerateSkillsPromptToOpenAIHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.prompt = self.db.get(Prompt, data['promptId'])
        self.topic = self.db.get(Topic, data['topicId'])


    def handle(self) -> GenerateSkillsResponseReceivedFromOpenAI:
        llm_client = get_llm_client()
        completion = llm_client.send_prompt(self.prompt)

        response = self._save_response_to_db(completion)

        return GenerateSkillsResponseReceivedFromOpenAI({
            **self.data,
            'responseId': response.id,
        })


    def _save_response_to_db(self, completion: Completion):
        properties = {
            'params': self.prompt.properties['params'],
        }

        response = Response(
            outline_id=self.data['outlineId'],
            prompt_id=self.prompt.id,
            role=completion.choices[0].message.role,
            payload=json.loads(completion.model_dump_json()),
            model=completion.model,
            prompt_tokens=completion.usage.prompt_tokens,
            completion_tokens=completion.usage.completion_tokens,
            total_tokens=completion.usage.total_tokens,
            content=completion.choices[0].message.content,
            properties=properties
        )

        self.db.add(response)
        self.db.commit()

        return response
