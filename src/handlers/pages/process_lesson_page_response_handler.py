from termcolor import colored
from db.db import DB, Outline, Response, Page
from ..mapping.map_page_content_to_nodes_handler import MapPageContentToNodesHandler
from ..validate_response_from_openai_handler import ValidateResponseFromOpenAIHandler
from src.events.event_manager import EVENT_MANAGER
from src.events.events import InvalidLessonPageResponseFromOpenAI, LessonPageResponseProcessedSuccessfully



class ProcessLessonPageResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.response = DB.get(Response, data['responseId'])
        self.page = DB.get(Page, data['pageId'])


    def handle(self) -> Outline:
        completion = self.response.payload

        validated_response = ValidateResponseFromOpenAIHandler(self.data).handle()

        if not validated_response:
            print(colored(f"Invalid response from OpenAI. Retrying...", "yellow"))
            return EVENT_MANAGER.trigger(InvalidLessonPageResponseFromOpenAI(self.data))

        content = self._add_header_to_page_content(completion)

        self._save_content_to_page(content)

        try:
            nodes = MapPageContentToNodesHandler({'pageId': self.page.id}).handle()
            self.page.update_properties(DB, {'nodes': nodes})
        except Exception as e:
            print(colored(f"Error parsing page nodes. Retrying... Error: {e}", "yellow"))
            return EVENT_MANAGER.trigger(InvalidLessonPageResponseFromOpenAI(self.data))

        return EVENT_MANAGER.trigger(
            LessonPageResponseProcessedSuccessfully(self.data)
        )


    def _add_header_to_page_content(self, completion: dict):
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


    def _save_content_to_page(self, material: str):
        content_hash = Page.hash_page(material)

        # Update page record
        self.page.content = material
        self.page.hash = content_hash
        self.page.link = self.page.permalink
        self.page.generated = True

        # Save to Database
        DB.commit()
