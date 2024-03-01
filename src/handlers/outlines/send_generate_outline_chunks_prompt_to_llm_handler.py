from db.db import DB, Outline, Thread, Prompt, Response
from ...llm.get_llm_client import get_llm_client
from termcolor import colored
from openai.types.completion import Completion
import progressbar



class SendGenerateOutlineChunksPromptsToLLMHandler:
    def __init__(self, data: dict):
        self.thread_id = data['threadId']
        self.outline = DB.get(Outline, data['outlineId'])
        self.prompts = DB.query(Prompt).filter(Prompt.id.in_(data['promptIds'])).all()
        self.topic = self.outline.topic



    def handle(self) -> list[int]:
        print(colored(f"\nGenerating {self.topic.name} outline_chunks...", "yellow"))

        response_ids = []
        prompt_count = len(self.prompts)
        llm_client = get_llm_client()

        with progressbar.ProgressBar(max_value=prompt_count, prefix='Generating outline chunk: ', redirect_stdout=True).start() as bar:
            for i, prompt in enumerate(self.prompts):
                messages = prompt.payload

                completion = llm_client.send_prompt('GenerateOutlineChunks', messages)
                if completion == None:
                    raise Exception("LLM completion failed. There is likely more output in the logs.")

                response = self._save_response_to_db(prompt, completion)
                response_ids.append(response.id)
                bar.update(i)

        return response_ids


    def _save_response_to_db(self, prompt: Prompt, completion: Completion):
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
