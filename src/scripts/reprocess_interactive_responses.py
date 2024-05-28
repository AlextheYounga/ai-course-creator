from sqlalchemy import text
from db.db import DB, EventStore
from src.handlers import ProcessMultipleChoiceInteractiveBatchResponseHandler, ProcessCodeEditorInteractiveResponseHandler, ProcessCodepenInteractiveResponseHandler

db = DB()


def reprocess_interactive_responses():
    events = db.query(EventStore).filter(
        EventStore.name.in_([
            'MultipleChoiceInteractiveBatchResponseReceivedFromOpenAI',
            'CodeEditorInteractiveResponseReceivedFromOpenAI',
            'CodepenInteractiveResponseReceivedFromOpenAI'
        ])
    )

    DB.execute(text(f"DELETE FROM interactive"))
    DB.commit()

    for event in events:
        match event.name:
            case 'MultipleChoiceInteractiveBatchResponseReceivedFromOpenAI':
                processed_event = ProcessMultipleChoiceInteractiveBatchResponseHandler(event.data).handle()
            case 'CodeEditorInteractiveResponseReceivedFromOpenAI':
                processed_event = ProcessCodeEditorInteractiveResponseHandler(event.data).handle()
            case 'CodepenInteractiveResponseReceivedFromOpenAI':
                processed_event = ProcessCodepenInteractiveResponseHandler(event.data).handle()

        print(f"{processed_event.__class__.__name__}: {processed_event.data['responseId']}")


reprocess_interactive_responses()
