from db.db import DB, Outline, Topic
from termcolor import colored
import sys
import inquirer

db = DB()


def select_outline(topic: Topic):
    outline_records = db.query(Outline)\
        .filter(Outline.topic_id == topic.id)\
        .order_by(Outline.id.desc())\
        .all()

    if len(outline_records) == 0:
        print(colored("No outlines found. Exiting...", "red"))
        sys.exit()

    outline_mapping = [
        {'name': outline.name, 'id': outline.id}
        for outline in outline_records
    ]

    outline_mapping[0]['name'] = f"{outline_mapping[0]['name']} (latest)"
    outline_names = [outline['name'] for outline in outline_mapping]

    outline_select = [
        inquirer.List('outlineSelect',
                      message=f"Select outline from {topic.name}",
                      choices=outline_names),
    ]

    user_prompt = inquirer.prompt(outline_select, raise_keyboard_interrupt=True)

    if user_prompt != None:
        answer = user_prompt['outlineSelect']

        selected_outline = [
            obj for obj in outline_mapping
            if obj['name'] == answer
        ][0]

        for record in outline_records:
            if record.id == selected_outline['id']:
                return record

        raise Exception("You did not select an outline. Exiting...")
