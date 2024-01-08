import shutil
import os
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from ..mocks.openai_mock_service import OpenAIMockService
from src.openai.outlines.generate_skills import SkillGenerator
from src.openai.outlines.draft_course_outline import OutlineDraft
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from src.utils.chat_helpers import slugify
from src.openai.page_material_creator import PageMaterialCreator

OUTPUT_PATH = "test/out"

# Reset output directory
slug = 'ruby-on-rails'
if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
    shutil.rmtree(f"{OUTPUT_PATH}/{slug}")





def create_outlines(topic: str):
    session_name = f"{topic} Outlines"
    ai_client = OpenAIMockService(session_name)

    # Generate Skills
    skill_generator = SkillGenerator(topic, ai_client, OUTPUT_PATH)
    skills = skill_generator.generate()

    # Generate Draft Outline
    draft = OutlineDraft(topic, ai_client, OUTPUT_PATH)
    draft_outline = draft.generate(skills)

    # Finalize Outline
    builder = MasterOutlineBuilder(topic, ai_client, OUTPUT_PATH)
    master_outline = builder.generate(draft_outline)

    course_list = [c['courseName'] for c in master_outline['courses']]
    return course_list


def create_page_material(topic: str):
    # Initialize OpenAI
    session_name = f"{topic} Page Material"
    ai_client = OpenAIMockService(session_name)

    creator = PageMaterialCreator(topic, ai_client, OUTPUT_PATH)
    outline = creator.create_pages_from_outline()

    return outline


def test_create_full_course():
    # Semi decent happy path test
    topics = ['Ruby on Rails']
    for topic in topics:
        # Begin creating course outlines
        course_list = create_outlines(topic)

        # Checking output
        assert len(course_list) == 15

        # Begin creating page material
        outline = create_page_material(topic)

        # Checking output
        assert len(os.listdir(f"{OUTPUT_PATH}/{slug}/content")) == 15

        for course in outline['courses']:
            course_slug = course['slug']
            assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}")

            for chapter in course['chapters']:
                chapter_slug = chapter['slug']
                assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}")

                for page in chapter['pages']:
                    page_slug = page['slug']
                    assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md")
