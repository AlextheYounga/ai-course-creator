import shutil
import os
from ..mocks.openai_mock_service import OpenAIMockService
from src.openai.outlines.generate_skills import SkillGenerator
from src.openai.outlines.draft_course_outline import OutlineDraft
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from src.openai.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.openai.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.openai.page_material_creator import PageMaterialCreator

OUTPUT_PATH = "test/out/course_material"

def _setup_test():
    # Reset output directory
    if (os.path.exists(f"{OUTPUT_PATH}")):
        shutil.rmtree(f"{OUTPUT_PATH}")

def _create_outlines(topic: str):
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

    course_list = [slug for slug in master_outline['courses']]
    return course_list


def _create_page_material(topic: str):
    session_name = f"{topic} Page Material"
    ai_client = OpenAIMockService(session_name)

    creator = PageMaterialCreator(topic, ai_client, OUTPUT_PATH)
    outline = creator.create_pages_from_outline()

    return outline


def _create_practice_skill_challenges(topic: str):
    session_name = f"{topic} Practice Skill Challenge"
    ai_client = OpenAIMockService(session_name)

    creator = PracticeSkillChallengeCreator(topic, ai_client, OUTPUT_PATH)
    outline = creator.create_practice_skill_challenges_for_chapters()

    return outline

def _create_final_skill_challenges(topic: str):
    session_name = f"{topic} Final Skill Challenge"
    ai_client = OpenAIMockService(session_name)

    creator = FinalSkillChallengeCreator(topic, ai_client, OUTPUT_PATH)
    outline = creator.create_final_skill_challenges_for_courses()

    return outline



def test_create_full_course():
    # Semi decent happy path test
    _setup_test()
    
    slug = 'ruby-on-rails'
    topics = ['Ruby on Rails']
    for topic in topics:
        # Begin creating course outlines
        course_list = _create_outlines(topic)

        # Checking output
        assert len(course_list) == 7

        # Begin creating page material
        outline = _create_page_material(topic)

        # Checking output
        assert len(os.listdir(f"{OUTPUT_PATH}/{slug}/content")) == 7

        for course_slug, course_data in outline['courses'].items():
            assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}")

            for chapter_slug, chapter_data in course_data['chapters'].items():
                assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}")

                for page_slug in chapter_data['pages']:
                    assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md")


        # Begin creating practice skill challenges
        outline = _create_practice_skill_challenges(topic)

        # Checking output
        for course_data in outline['courses'].values():
            for chapter_data in course_data['chapters'].values():
                paths = chapter_data['paths']
                page_names = [p.split('/')[-1] for p in paths]
                challenge_pages = [p for p in page_names if 'challenge' in p]

                assert len(challenge_pages) == 1

        
        # Begin creating final skill challenges
        outline = _create_final_skill_challenges(topic)

        # Checking output
        for course in outline['courses']:
            assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course}/final-skill-challenge/final-skill-challenge.md")
