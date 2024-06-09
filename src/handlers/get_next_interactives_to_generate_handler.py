from db.db import DB, Topic, Outline, OutlineEntity, Page, Interactive
from src.events.events import GenerateCodepenPageInteractivesProcessStarted, GenerateCodeEditorPageInteractivesProcessStarted, GenerateMultipleChoicePageInteractivesProcessStarted, PageInteractivesGenerationComplete


class GetNextInteractivesToGenerateHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.page = self.db.get(Page, data['pageId'])
        self.topic = self.db.get(Topic, data['topicId'])


    def handle(self):
        interactives_to_generate = self.data['interactives']
        generated_interactives = self._get_generated_page_interactives()

        for key in interactives_to_generate:
            generated_count = len([i for i in generated_interactives if i.type == key])
            interactives_to_generate[key] -= generated_count

        # Remove zero values from dict
        interactives_to_generate = {k: v for k, v in interactives_to_generate.items() if v > 0}

        if not interactives_to_generate:
            return PageInteractivesGenerationComplete({
                **self.data,
                'interactiveIds': [i.id for i in generated_interactives]
            })

        next_type_to_generate = next(iter(interactives_to_generate))
        self.data.update({
            'interactives': interactives_to_generate
        })

        match next_type_to_generate:
            case 'multipleChoice':
                return GenerateMultipleChoicePageInteractivesProcessStarted(self.data)

            case 'codeEditor':
                return GenerateCodeEditorPageInteractivesProcessStarted(self.data)

            case 'codepen':
                return GenerateCodepenPageInteractivesProcessStarted(self.data)
            case _:
                raise Exception(f"Interactive type {next_type_to_generate} not found")


    def _get_generated_page_interactives(self):
        return self.db.query(Interactive).filter(
            Interactive.page_source_id == self.page.id
        ).all()
