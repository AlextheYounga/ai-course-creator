from pydoc import locate
from termcolor import colored
from db.db import DB, EventStore
from .event_mapping import EVENT_HANDLER_MAPPING


class BaseEvent:
    def __init__(self):
        self.data = None
        self.id = None
        self.db = DB()
        self.handler = None
        self.status = "pending"


    @classmethod
    def trigger(cls, event):
        print(colored(event.__class__.__name__, "green"))

        event.handler = event.get_handler()
        event.save()  # Save event to the database
        if not event.handler: return None

        next_events = event.handler.handle()
        if not next_events: return None

        if not isinstance(next_events, list):
            next_events = [next_events]

        return next_events


    # Currently prevents the ability to have subfolders inside the handlers folder
    def get_handler(self):
        event_name = self.__class__.__name__
        if event_name in EVENT_HANDLER_MAPPING:
            handler_name = EVENT_HANDLER_MAPPING[event_name]
            handler = locate(f'src.handlers.{handler_name}')
            return handler(self.data)

        return None


    def serialize(self):
        return {
            'eventId': self.id,
            'eventName': self.__class__.__name__,
            'eventData': self.data,
        }


    @classmethod
    def deserialize_from_job(cls, job):
        # Get event data
        event_name = job.data['eventName']
        event_id = job.data.get('eventId', None)
        event_data = job.data.get('eventData', {})
        event_data.update({'jobId': job.id})

        # Create the event instance
        event = locate(f'src.events.events.{event_name}')(event_data, event_id)
        event.status = job.status

        return event


    def save(self):
        self.handler = self.get_handler()
        handler_name = self.handler.__class__.__name__ if self.handler else None

        event_store = EventStore(
            name=self.__class__.__name__,
            job_id=self.data.get('jobId', None),
            handler=handler_name,
            data=self.data
        )

        self.db.add(event_store)
        self.db.commit()

        return event_store
