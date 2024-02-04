import inquirer
from db.db import DB, Topic
from .select_topic import select_topic
from .select_generate_content import select_generate_content
from .select_regenerate_content import select_regenerate_content
from ..utils import dump_outline_content
from .generate_functions import generate_outline


def run_dump_outline_content(topic: Topic):
    outline = topic.get_latest_outline()
    return dump_outline_content(outline)


def select_subroutine():
    topic_name = select_topic()
    topic = Topic.first_or_create(DB, name=topic_name)

    base_subroutines = {
        'Generate Outline': generate_outline,
        'Generate Content': select_generate_content,
        'Regenerate Content': select_regenerate_content,
        'Dump Content From Existing Outline': run_dump_outline_content,
    }

    subroutines = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=list(base_subroutines.keys())),
    ]

    choice = inquirer.prompt(subroutines)
    subroutine = choice['subroutine']
    subroutine_function = base_subroutines[subroutine]

    # Dynamic function call
    subroutine_function(topic)
    print('Done')
