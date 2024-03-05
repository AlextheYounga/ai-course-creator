
from .events import Event
from ..utils.log_handler import LOG_HANDLER


class EventManager:
    def __init__(self):
        self.handlers = {}

    def subscribe(self, events: list[Event], handler):
        for event_type in events:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

    def trigger(self, event: Event):
        event_type = type(event)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                self.__log_event(event, handler)
                handler(data=event.data).handle()
        else:
            self.__log_event(event, None)

    def __log_event(self, event: Event, handler):
        message = ""
        event_name = event.__class__.__name__

        for key, value in event.data.items():
            message += f"{key}: {value} "

        if handler:
            handler_name = handler.__name__
            message = f"{event_name} -> {handler_name} | Data: {message}"
        else:
            message = f"{event_name} | Data: {message}"

        LOG_HANDLER.info(message)


EVENT_MANAGER = EventManager()
