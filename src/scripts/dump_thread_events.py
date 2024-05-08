from db.db import DB, EventStore
from sqlalchemy import Integer
from termcolor import colored
from .cli.select.select_jobstore import select_job
import sys




def dump_job_events():
    job = select_job()

    job_properties = job.properties or {}
    event_handlers = job_properties.get('eventHandlers', [])
    if not event_handlers:
        print(colored("No event handlers found. Exiting...", "red"))
        sys.exit()

    events = DB.query(EventStore).filter(
        EventStore.data['jobId'].cast(Integer) == job.id
    ).order_by(
        EventStore.id.asc()
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


dump_job_events()
