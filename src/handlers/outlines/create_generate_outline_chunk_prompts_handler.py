from db.db import DB, Outline, Prompt
from src.events.event_manager import EVENT_MANAGER
from src.events.events import AllGenerateOutlineChunksPromptsCreated
from ...llm.get_prompt import get_prompt
from ...utils.chunks import chunks_list
from ...llm.get_llm_params import get_llm_params
from ...llm.token_counter import count_tokens_using_encoding
import yaml


class CreateAllOutlineChunkPromptsHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.topic = self.outline.topic
        self.prompt_subject = 'outline'  # corresponds with key in params.yaml


    def handle(self):
        llm_params = get_llm_params(self.prompt_subject)
        model = llm_params['model']

        skills = self.outline.properties.get('skills', None)
        if skills == None:
            raise Exception("Skills are required to generate outlines.")

        skill_chunks = chunks_list(skills, 2)
        prompt_ids = []

        for chunk in skill_chunks:
            messages = self._build_generate_outline_chunks_prompts(chunk)
            tokens = count_tokens_using_encoding(model, messages)

            prompt = self._save_prompt(messages, tokens, llm_params)
            prompt_ids.append(prompt.id)

        return EVENT_MANAGER.trigger(
            AllGenerateOutlineChunksPromptsCreated({
                'threadId': self.thread_id,
                'outlineId': self.outline.id,
                'promptIds': prompt_ids,
                'topicId': self.topic.id,
            }))


    def _build_generate_outline_chunks_prompts(self, skills_chunk: dict) -> list[dict]:
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        skills_system_prompt = get_prompt(self.topic, 'system/outlines/tune-skills', {
            'topic': self.topic.name,
            'skills': yaml.dump(skills_chunk)
        })

        outline_chunks_prompt = ''
        if self.outline.properties.get('outline_chunks', False):
            outline_chunks_prompt = get_prompt(self.topic, 'system/outlines/tune-outline-chunks', {
                'chunks': yaml.dump(self.outline.properties['outline_chunks'])
            })

        system_tuning_prompt = "\n".join([skills_system_prompt, outline_chunks_prompt])
        combined_system_prompt = "\n".join([general_system_prompt, system_tuning_prompt])
        user_prompt = get_prompt(self.topic, 'user/outlines/outline-chunk', {'topic': self.topic.name})

        return [
            {"role": "system", "content": combined_system_prompt},
            {"role": "user", "content": user_prompt}
        ]


    def _save_prompt(self, messages: list[dict], tokens: int, params: dict) -> Prompt:
        content = ""
        for message in messages:
            content += message['content'] + "\n\n"

        properties = {
            'params': params,
        }

        prompt = Prompt(
            thread_id=self.thread_id,
            outline_id=self.outline.id,
            subject=self.prompt_subject,
            model=properties['params']['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        DB.add(prompt)
        DB.commit()

        return prompt
