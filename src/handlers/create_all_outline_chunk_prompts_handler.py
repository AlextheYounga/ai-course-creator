import yaml
from db.db import DB, Topic, Outline, Prompt
from src.events.events import AllGenerateOutlineChunksPromptsCreated
from ..utils.llm.get_prompt import get_prompt
from ..utils.chunks import chunks_list
from ..utils.llm.get_llm_params import get_llm_params
from ..utils.llm.token_counter import count_token_estimate



class CreateAllOutlineChunkPromptsHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.topic = self.db.get(Topic, data['topicId'])
        self.prompt_subject = 'outline'  # corresponds with key in configs/params.yaml


    def handle(self):
        llm_params = get_llm_params(self.prompt_subject)
        skills = self.outline.get_properties('skills')
        if skills == None:
            raise Exception("Skills are required to generate outlines.")

        skill_chunks = chunks_list(skills, 2)
        prompt_ids = []

        for chunk in skill_chunks:
            messages = self._build_generate_outline_chunks_prompts(chunk)
            tokens = count_token_estimate(messages)

            prompt = self._save_prompt(messages, tokens, llm_params)
            prompt_ids.append(prompt.id)


        self.outline.update_properties(self.db, {'promptChunkIds': prompt_ids})

        return AllGenerateOutlineChunksPromptsCreated({
            **self.data,
        })


    def _build_generate_outline_chunks_prompts(self, skills_chunk: dict) -> list[dict]:
        general_system_prompt = get_prompt(self.topic, 'system/general', {'topic': self.topic.name})
        skills_system_prompt = get_prompt(self.topic, 'system/outlines/skills-context', {
            'topic': self.topic.name,
            'skills': yaml.dump(skills_chunk)
        })

        outline_chunks_prompt = ''
        outline_properties = self.outline.properties or {}
        if outline_properties.get('outline_chunks', False):
            outline_chunks_prompt = get_prompt(self.topic, 'system/outlines/outline-chunks-context', {
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
            outline_id=self.outline.id,
            subject=self.prompt_subject,
            model=properties['params']['model'],
            content=content,
            payload=messages,
            estimated_tokens=tokens,
            properties=properties,
        )

        self.db.add(prompt)
        self.db.commit()

        return prompt
