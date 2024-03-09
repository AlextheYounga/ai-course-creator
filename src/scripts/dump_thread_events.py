from db.db import DB, Event
from sqlalchemy import Integer
from termcolor import colored
from .cli.select_thread import select_thread
import sys




def dump_thread_events():
    thread = select_thread()

    event_handlers = thread.properties.get('eventHandlers', [])
    if not event_handlers:
        print(colored("No event handlers found. Exiting...", "red"))
        sys.exit()

    events = DB.query(Event).filter(
        Event.data['threadId'].cast(Integer) == thread.id
    ).order_by(
        Event.id.asc()
    ).all()

    space = ' '
    retab = False
    last_event = None
    for i, event in enumerate(events):
        if i == 0:
            print(colored(event.name, "green"))
        else:
            print(colored('|' + space + event.name, "green"))

        if retab == True:
            space = ' '
            retab = False
            continue


        space = space + '  '

        if event.handler:
            if ((last_event) and (last_event in event_handlers) and (event.handler in event_handlers[last_event])):
                space = space + '  '

            print(colored('|' + space + event.handler, "yellow"))
        else:
            retab = True

        last_event = event.name

    print(colored(f"\nEvent count: {len(events)}", "green"))


dump_thread_events()
