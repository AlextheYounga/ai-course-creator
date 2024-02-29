from db.db import DB, Outline, Thread, Prompt, Response
from ...llm.get_llm_client import get_llm_client
from ...utils.log_handler import LOG_HANDLER
from termcolor import colored
from openai.types.completion import Completion
import progressbar
import json



class SendGenerateSkillsPromptHandler:
    def __init__(self, thread_id: int, outline_id: int, prompt_ids: list[int]):
        self.thread = DB.get(Thread, thread_id)
        self.outline = DB.get(Outline, outline_id)
        self.prompts = DB.query(Prompt).filter(Prompt.id.in_(prompt_ids)).all()
        self.topic = self.outline.topic
        self.logger = LOG_HANDLER.getLogger(self.__class__.__name__)


    def handle(self):
        print(colored(f"\nGenerating {self.topic.name} outline_chunks...", "yellow"))

        response_ids = []
        prompt_count = len(self.prompts)
        llm_client = get_llm_client()

        with progressbar.ProgressBar(max_value=prompt_count, prefix='Generating outline chunk: ', redirect_stdout=True).start() as bar:
            for i, prompt in enumerate(self.prompts):
                messages = prompt.payload

                completion = llm_client.send_prompt('generate-outline-chunks', messages)
                if completion == None:
                    raise Exception("LLM completion failed. There is likely more output in the logs.")

                response = self._save_response_payload_to_db(completion)
                response_ids.append(response.id)
                bar.update(i)

        return response_ids


    def _save_response_payload_to_db(self, completion: Completion):
        # We only save the payload for now, we will process this later.
        response = Response(
            prompt_id=self.prompt.id,
            role=completion.choices[0].message.role,
            payload=json.loads(completion.model_dump_json()),
        )
        DB.add(response)
        DB.commit()

        return response
