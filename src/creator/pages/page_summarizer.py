from dotenv import load_dotenv
from termcolor import colored
from src.creator.helpers import get_prompt
from openai import OpenAI
from db.db import DB, Page


load_dotenv()


class PageSummarizer():
    def __init__(self, page: Page, client: OpenAI):
        self.page = page
        self.ai_client = client


    # Main


    def summarize(self):
        messages = self.build_summarize_page_prompt()

        options = {'quiet': True}

        # Send to ChatGPT
        print(colored(f"Sending summarize-page prompt for {self.page.name}", "cyan"))
        completion = self.ai_client.send_prompt('summarize-page', messages, options=options)
        summary = completion['content']

        self.page.summary = summary
        DB.commit()

        return self.page


    # Prompts


    def build_summarize_page_prompt(self):
        topic = self.page.topic
        summarize_prompt = get_prompt(topic, 'user/pages/summarize', [("{content}", self.page.content)])

        return [
            {"role": "user", "content": summarize_prompt},
        ]
