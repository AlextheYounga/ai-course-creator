from termcolor import colored
from db.db import DB, Outline, Response, Page, Interactive
from .validate_response_from_openai_handler import ValidateResponseFromOpenAIHandler
from src.events.events import InvalidLessonPageResponseFromOpenAI, LessonPageResponseProcessedSuccessfully, GeneratePageInteractivesJobRequested


class ProcessLessonPageResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.page = self.db.get(Page, data['pageId'])


    def handle(self) -> Outline:
        content = self.response.content

        # Check response for blatant problems
        validated_response = ValidateResponseFromOpenAIHandler(self.data).handle()

        if not validated_response:
            print(colored(f"Invalid response from OpenAI. Retrying...", "yellow"))
            return InvalidLessonPageResponseFromOpenAI(self.data)

        content = self._add_header_to_page_content(content)

        self._save_content_to_page(content)

        return LessonPageResponseProcessedSuccessfully(self.data)

    def _add_header_to_page_content(self, content: str):
        # If page does not have a header, add one
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


    def _delete_existing_page_interactives_for_regeneration(self):
        existing_interactives = self.db.query(Interactive).filter(
            Interactive.page_source_id == self.page.id
        ).all()

        for interactive in existing_interactives:
            self.db.delete(interactive)

        self.db.commit()


    def _save_content_to_page(self, material: str):
        content_hash = Page.hash_page(material)

        # Update page record
        self.page.content = material
        self.page.hash = content_hash
        self.page.generated = True

        # Save to Database
        self.db.commit()
