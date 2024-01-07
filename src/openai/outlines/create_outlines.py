import os
from termcolor import colored
from ..openai_handler import OpenAiHandler
from .generate_skills import SkillGenerator
from .draft_course_outline import OutlineDraft
from .build_master_outline import MasterOutlineBuilder
from src.utils.files import read_json_file
from src.utils.chat_helpers import slugify
import inquirer


def check_for_existing_outlines(topic):
    topic_formatted = slugify(topic)
    course_material_path = f"src/data/chat/course_material/{topic_formatted}"
    existing = os.path.exists(f"{course_material_path}/master-outline.json")

    if (existing):
        print(colored(f"Course outline for {topic} already exists.", "yellow"))
        return False
    return True


def process_topics(topics: list[str]):
    # Generate series list of courses
    for topic in topics:
        session_name = f"{topic} Outlines"
        ai_client = OpenAiHandler(session_name)
        existing = check_for_existing_outlines(topic)

        if not existing:
            # Generate Skills
            skill_generator = SkillGenerator(topic, ai_client)
            skills = skill_generator.generate()

            # Generate Draft Outline
            draft = OutlineDraft(topic)
            draft_outline = draft.generate(skills['yaml'])

            # Finalize Outline
            builder = MasterOutlineBuilder(topic, ai_client)
            master_outline = builder.generate(draft_outline['yaml'])

            course_list = [c['courseName'] for c in master_outline]
            print(colored("Course list: ", "green"))
            print(colored("\n".join(course_list), "green"))

    print(colored("\nAll outlines complete.", "green"))


def create_outlines():
    try:
        topics = read_json_file("src/data/topics.json")
        topic_choices = ['All'] + topics

        choices = [
            inquirer.List('topic',
                          message="Which topic would you like to generate outlines for?",
                          choices=topic_choices),
        ]

        choice = inquirer.prompt(choices)
        if choice != None:
            answer = choice['topic']

            if answer == 'All':
                process_topics(topics)
            else:
                process_topics([answer])

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    create_outlines()
