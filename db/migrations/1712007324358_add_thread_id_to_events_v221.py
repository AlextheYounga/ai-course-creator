from sqlalchemy import text
from termcolor import colored
from db.db import DB, Event


def up():
    try:
        # Add the column
        DB.execute(text(
            """
            ALTER TABLE event 
            ADD COLUMN thread_id INTEGER
            AFTER id;
            """
        ))

        DB.commit()


        # Add index
        DB.execute(text(
            """
            CREATE INDEX ix_event_thread_id ON event (thread_id);
            """
        ))

        DB.commit()
    except Exception as e:
        DB.rollback()
        print(colored(e, "red"))


    # Post migration script
    try:
        # Get a mapping of all event ids to their respective thread ids
        event_id_thread_mapping = {}

        events = DB.query(Event).all()
        for event in events:
            thread_id = event.get_data().get("threadId", False)
            if thread_id:
                event_id_thread_mapping[event.id] = thread_id

        # Update all event with the thread_id
        for event_id, thread_id in event_id_thread_mapping.items():
            DB.query(Event).filter(Event.id == event_id).update({"thread_id": thread_id})

        DB.commit()

    except Exception as e:
        DB.rollback()
        print(colored(e, "red"))
