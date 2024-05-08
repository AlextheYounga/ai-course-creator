import collections
from db.db import DB, Outline, Response
from src.events.events import AllOutlineChunkResponsesProcessedSuccessfully, OutlineChunkGenerationProcessStarted


class GetNextOutlineChunkPromptHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])

    def handle(self):
        prompts_to_send = self.outline.get_properties().get('promptChunkIds', [])

        if len(prompts_to_send) == 0:
            raise Exception("No prompts found for this outline")

        prompts_sent, response_ids = self._get_all_prompts_already_sent(prompts_to_send)
        all_prompts_sent = collections.Counter(prompts_sent) == collections.Counter(prompts_to_send)

        if all_prompts_sent:
            return AllOutlineChunkResponsesProcessedSuccessfully({
                **self.data,
                'promptIds': prompts_sent,
                'responseIds': response_ids,
            })

        next_prompt_to_send_id = None
        for prompt_id in prompts_to_send:
            if prompt_id not in prompts_sent:
                next_prompt_to_send_id = prompt_id
                break

        total_prompts_to_generate = len(prompts_to_send)

        return OutlineChunkGenerationProcessStarted(data={
            **self.data,
            'promptId': next_prompt_to_send_id,
            'totalSteps': total_prompts_to_generate,
        })






    def _get_all_prompts_already_sent(self, prompts_to_send: list[int]):
        responses = self.db.query(Response).filter(Response.prompt_id.in_(prompts_to_send)).all()
        sent_prompt_ids = [r.prompt_id for r in responses]
        response_ids = [r.id for r in responses]

        return sent_prompt_ids, response_ids
