from termcolor import colored
from db.db import DB, Outline, Response, Page
from .validate_response_from_openai_handler import ValidateResponseFromOpenAIHandler
from src.events.events import InvalidLessonPageResponseFromOpenAI, LessonPageResponseProcessedSuccessfully, GeneratePageInteractivesJobRequested


class ProcessLessonPageResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.page = self.db.get(Page, data['pageId'])
        self.next_events = []


    def handle(self) -> Outline:
        completion = self.response.payload

        # Check response for blatant problems
        validated_response = ValidateResponseFromOpenAIHandler(self.data).handle()

        if not validated_response:
            print(colored(f"Invalid response from OpenAI. Retrying...", "yellow"))
            return InvalidLessonPageResponseFromOpenAI(self.data)

        content = self._add_header_to_page_content(completion)

        self._save_content_to_page(content)
        self.next_events.append(LessonPageResponseProcessedSuccessfully(self.data))

        if self._topic_permits_interactives():  # true by default
            self.next_events.append(GeneratePageInteractivesJobRequested(self.data))  # Async job flow

        return self.next_events

    def _add_header_to_page_content(self, completion: dict):
        # If page does not have a header, add one
        content = completion['choices'][0]['message']['content']

        # If header is h1, do nothing
        if content[:2] == '# ': return content

        # If header is h2, make h1
        if content[:3] == '## ':
            split_content = content.split('## ', 1)[1]
            content = '# ' + split_content

        # If header is h3, make h1
        if content[:3] == '### ':
            split_content = content.split('## ', 1)[1]
            content = '# ' + split_content

        if content[:2] != '# ':
            header = f"# {self.page.name}\n"
            content = header + content

        return content


    def _topic_permits_interactives(self):
        return self.page.topic.get_properties().get('settings', {}).get('hasInteractives', True)


    def _save_content_to_page(self, material: str):
        content_hash = Page.hash_page(material)

        # Update page record
        self.page.content = material
        self.page.hash = content_hash
        self.page.generated = True

        # Save to Database
        self.db.commit()
