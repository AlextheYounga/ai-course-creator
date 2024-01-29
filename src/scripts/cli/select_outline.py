from db.db import DB, Outline, Topic
import inquirer



def select_outline(topic):
    topic_record = DB.query(Topic).filter(Topic.name == topic).first()

    outline_records = DB.query(Outline)\
        .filter(Outline.topic_id == topic_record.id)\
        .order_by(Outline.id.desc())\
        .all()

    outlines = [outline.name for outline in outline_records]
    outlines[0] = f"{outlines[0]} (latest)"

    outline_select = [
        inquirer.List('outlineSelect',
                      message=f"Select outline from {topic_record.name}",
                      choices=outlines),
    ]

    user_prompt = inquirer.prompt(outline_select)

    if user_prompt != None:
        answer = user_prompt['outlineSelect']

        for record in outline_records:
            if record.name in answer:
                return record

        raise Exception("You did not select an outline. Exiting...")
