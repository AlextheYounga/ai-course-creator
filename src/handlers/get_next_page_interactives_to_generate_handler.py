from db.db import DB, Topic, Outline, OutlineEntity, Page, Interactive
from src.events.events import GenerateCodepenPageInteractiveProcessStarted, GenerateCodeEditorPageInteractiveProcessStarted, GenerateMultipleChoicePageInteractivesProcessStarted, PageInteractivesGenerationComplete


class GetNextPageInteractivesToGenerateHandler:
    """
    This handler is responsible for determining the next interactive type to generate for a page.
    Interactive job events are dispatched synchronously, where only one is dispatched at a time, and
    when that job flow is completed, we will check again for the next interactive type to generate.
    """
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.page = self.db.get(Page, data['pageId'])
        self.topic = self.db.get(Topic, data['topicId'])


    def handle(self):
        page_interactives_to_generate = self.data['interactives']
        generated_interactives = self._get_generated_page_interactives()

        # Subtract generated interactives from interactives to generate
        for generated_interactive in generated_interactives:
            if generated_interactive.type in page_interactives_to_generate:
                page_interactives_to_generate[generated_interactive.type] -= 1

                # Remove from dict if count is 0
                if page_interactives_to_generate[generated_interactive.type] <= 0:
                    del page_interactives_to_generate[generated_interactive.type]


        # Get next interactive type to generate
        interactive_type = None
        for typ, count in page_interactives_to_generate.items():
            if count > 0:
                interactive_type = typ
                break

        if not page_interactives_to_generate or not interactive_type:
            return PageInteractivesGenerationComplete({
                **self.data,
                'interactiveIds': [i.id for i in generated_interactives]
            })

        match interactive_type:
            case 'multipleChoice':
                # Multiple choice interactives can be handled as a batch
                return GenerateMultipleChoicePageInteractivesProcessStarted(self.data)

            case 'codeEditor':
                return GenerateCodeEditorPageInteractiveProcessStarted(self.data)

            case 'codepen':
                return GenerateCodepenPageInteractiveProcessStarted(self.data)
            case _:
                raise Exception(f"Interactive type {interactive_type} not found")


    def _get_generated_page_interactives(self):
        page_outline_entity_id = self.db.query(OutlineEntity.id).filter(
            OutlineEntity.entity_id == self.page.id,
            OutlineEntity.entity_type == 'Page',
            OutlineEntity.outline_id == self.data['outlineId']
        ).first()[0]  # returns as tuple

        return self.db.query(Interactive).filter(
            Interactive.outline_entity_id == page_outline_entity_id
        ).all()
