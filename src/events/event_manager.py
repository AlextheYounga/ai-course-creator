
from .events import Event
from termcolor import colored


class EventManager:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, events: list[Event], handler):
        for event_type in events:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

    def trigger(self, event: Event):
        print(colored(f"Handling event: {self.event.__class__.__name__}", "green"))
        event_type = type(event)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(data=event.data)


EVENT_MANAGER = EventManager()
