from sqlalchemy import text
from db.db import DB, EventStore
from src.handlers import ProcessMultipleChoiceInteractivesResponseHandler, ProcessCodeEditorInteractivesResponseHandler, ProcessCodepenInteractivesResponseHandler

db = DB()


def reprocess_interactive_responses():
    events = db.query(EventStore).filter(
        EventStore.name.in_([
            'MultipleChoiceInteractiveResponseReceivedFromOpenAI',
            'CodeEditorInteractiveResponseReceivedFromOpenAI',
            'CodepenInteractiveResponseReceivedFromOpenAI'
        ])
    )

    db.execute(text(f"DELETE FROM interactive"))
    db.commit()

    for event in events:
        match event.name:
            case 'MultipleChoiceInteractiveResponseReceivedFromOpenAI':
                processed_event = ProcessMultipleChoiceInteractivesResponseHandler(event.data).handle()
            case 'CodeEditorInteractiveResponseReceivedFromOpenAI':
                processed_event = ProcessCodeEditorInteractivesResponseHandler(event.data).handle()
            case 'CodepenInteractiveResponseReceivedFromOpenAI':
                processed_event = ProcessCodepenInteractivesResponseHandler(event.data).handle()

        print(f"{processed_event.__class__.__name__}: {processed_event.data['responseId']}")


reprocess_interactive_responses()
