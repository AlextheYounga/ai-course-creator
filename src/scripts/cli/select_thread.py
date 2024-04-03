import sys
import inquirer
from termcolor import colored
from db.db import DB, Thread


def select_thread():
    thread_records = DB.query(Thread).order_by(
        Thread.id.desc()
    ).all()

    if len(thread_records) == 0:
        print(colored("No threads found. Exiting...", "red"))
        sys.exit()

    thread_mapping = [
        {'name': f"{thread.name} - {thread.created_at}", 'id': thread.id}
        for thread in thread_records
    ]

    thread_mapping[0]['name'] = f"{thread_mapping[0]['name']} (latest)"
    thread_names = [thread['name'] for thread in thread_mapping]

    thread_select = [
        inquirer.List('threadSelect',
                      message=f"Select thread",
                      choices=thread_names),
    ]

    user_prompt = inquirer.prompt(thread_select)

    if user_prompt != None:
        answer = user_prompt['threadSelect']

        selected_thread = [
            obj for obj in thread_mapping
            if obj['name'] == answer
        ][0]

        for record in thread_records:
            if record.id == selected_thread['id']:
                return record

        raise Exception("You did not select an outline. Exiting...")
