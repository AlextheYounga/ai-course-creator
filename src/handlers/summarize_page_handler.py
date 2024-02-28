from db.db import DB, Page
from termcolor import colored
from ..utils.prompts import get_prompt
from openai import OpenAI


class SummarizePageHandler():
    def __init__(self, page: Page, llm: OpenAI):
        self.page = page
        self.llm_hander = llm

    def handle(self):
        messages = self._build_summarize_page_simple_prompt()

        options = {'quiet': True}

        # Send to ChatGPT
        print(colored(f"Sending summarize-page prompt for {self.page.name}", "cyan"))
        completion = self.llm_hander.send_prompt('summarize-page', messages, options=options)
        summary = completion['content']

        self.page.summary = summary
        DB.commit()

        return self.page


    def _build_summarize_page_simple_prompt(self):
        topic = self.page.topic
        summarize_prompt = get_prompt(topic, 'user/pages/summarize', {'content': self.page.content})

        return [
            {"role": "user", "content": summarize_prompt},
        ]
