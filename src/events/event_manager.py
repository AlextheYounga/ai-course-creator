from db.db import DB, Event as EventStore
from .events import Event
from ..utils.log_handler import LOG_HANDLER
from ..utils.event_progressbar import EventProgressbar


class EventManager:
    def __init__(self):
        self.handlers = {}
        self.show_progress = False
        self.progressbar = None

    def subscribe(self, events: list[Event], handler):
        for event_type in events:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

    def trigger(self, event: Event):
        event_type = type(event)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                self.__run_accessory_event_functions(event, handler)

                handler(data=event.data).handle()
        else:
            self.__run_accessory_event_functions(event, None)


    def refresh(self):
        self.handlers = {}


    def dump_handlers(self):
        handlers = {}
        for event, handler in self.handlers.items():
            handlers[event.__name__] = [h.__name__ for h in handler]
        return handlers


    def __run_accessory_event_functions(self, event: Event, handler):
        self.__log_event(event, handler)
        self.__save_event(event, handler)
        self.__update_progress(event)


    def __save_event(self, event: Event, handler):
        handler = handler.__name__ if handler else None

        event_store = EventStore(
            name=event.__class__.__name__,
            handler=handler,
            data=event.data
        )

        DB.add(event_store)
        DB.commit()


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


    def __update_progress(self, event: Event):
        if self.show_progress:
            if self.progressbar == None:
                thread_id = event.data['threadId']

                max_value = event.data.get('totalSteps', False) # We need a total to show the progress bar
                if not max_value:
                    return
                
                self.progressbar = EventProgressbar(thread_id).start(event)
        
            self.progressbar.update_on_event(event)


EVENT_MANAGER = EventManager()
