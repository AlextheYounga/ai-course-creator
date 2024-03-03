from db.db import DB, Outline, Prompt, Response
from src.events.event_manager import EVENT_MANAGER
from src.events.events import GenerateSkillsPromptSentToLLM
from ...llm.get_llm_client import get_llm_client
from termcolor import colored
from openai.types.completion import Completion



class SendGenerateSkillsPromptToLLMHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.prompt = DB.get(Prompt, data['promptId'])
        self.topic = self.outline.topic


    def handle(self) -> GenerateSkillsPromptSentToLLM:
        print(colored(f"\nGenerating {self.topic.name} skills...", "yellow"))

        messages = self.prompt.payload

        # Send to ChatGPT
        llm_client = get_llm_client()
        completion = llm_client.send_prompt('GenerateSkills', messages)

        response = self._save_response_to_db(completion)

        return self.__trigger_completion_event({
            'threadId': self.thread_id,
            'outlineId': self.outline.id,
            'topicId': self.topic.id,
            'promptId': self.prompt.id,
            'responseId': response.id,
        })


    def _save_response_to_db(self, completion: Completion):
        properties = {
            'params': self.prompt.properties['params'],
        }

        response = Response(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            prompt_id=self.prompt.id,
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

    def __trigger_completion_event(self, data: dict):
        EVENT_MANAGER.trigger(GenerateSkillsPromptSentToLLM(data))
