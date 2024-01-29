import os
from dotenv import load_dotenv
from termcolor import colored
from src.creator.helpers import get_prompt
from openai import OpenAI
from db.db import DB, Page
from src.utils.strings import string_hash


load_dotenv()


class PageSummarizer():
    def __init__(self, page: Page, client: OpenAI):
        self.page = page
        self.ai_client = client


    def build_summarize_page_prompt(self):
        summarize_prompt = get_prompt('user/pages/summarize', [("{content}", self.page.content)])
        return [
            {"role": "user", "content": summarize_prompt},
        ]


    def summarize(self):
        model = 'gpt-3.5-turbo-0301'  # Fastest model

        messages = self.build_summarize_page_prompt()

        options = {
            'model': model,
            'maxTokens': 100,
            'quiet': True,
        }

        # Send to ChatGPT
        print(colored(f"Sending summarize-page prompt for {self.page.name}", "cyan"))
        completion = self.ai_client.send_prompt('summarize-page', messages, options=options)
        summary = completion['content']

        self.page.summary = summary
        DB.add(self.page)
        DB.commit()

        return self.page
