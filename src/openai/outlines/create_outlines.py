import os
from termcolor import colored
from ..openai_handler import OpenAiHandler
from .generate_skills import SkillGenerator
from .draft_course_outline import OutlineDraft
from .build_master_outline import MasterOutlineBuilder
from src.utils.files import read_json_file
from src.utils.chat_helpers import slugify
import inquirer


COURSE_MATERIAL_PATH = f"out/course_material"


def check_for_existing_outlines(topic):
    topic_slug = slugify(topic)
    course_material_path = f"out/course_material/{topic_slug}"
    existing = os.path.exists(f"{course_material_path}/master-outline.json")

    if (existing):
        print(colored(f"Course outline for {topic} already exists.", "yellow"))
        return True
    return False


def main(topics: list[str]):
    # Generate series list of courses
    for topic in topics:
        session_name = f"{topic} Outlines"
        ai_client = OpenAiHandler(session_name)
        existing = check_for_existing_outlines(topic)

        if not existing:
            # Generate Skills
            skill_generator = SkillGenerator(topic, ai_client, COURSE_MATERIAL_PATH)
            skills = skill_generator.generate()

            # Generate Draft Outline
            draft = OutlineDraft(topic, ai_client, COURSE_MATERIAL_PATH)
            draft_outline = draft.generate(skills)

            # Finalize Outline
            builder = MasterOutlineBuilder(topic, ai_client, COURSE_MATERIAL_PATH)
            master_outline = builder.generate(draft_outline)

            course_list = [course['courseName'] for course in master_outline['courses'].values()]

            print(colored("\nCourse list: ", "green"))
            print(colored("\n".join(course_list), "green"))

    print(colored("\nAll outlines complete.\n", "green"))


def cli_prompt_user():
    try:
        topics = read_json_file("data/topics.json")
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
                main(topics)
            else:
                main([answer])

    except KeyboardInterrupt:
        print(colored("Exiting...", "red"))


if __name__ == "__main__":
    cli_prompt_user()
