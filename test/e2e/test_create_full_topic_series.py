import shutil
import os
from ..mocks.openai_mock_service import OpenAIMockService
from ..mocks.db import *
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator

DB = setup_db()
OUTPUT_PATH = "test/out"


def _setup_test():
    # Reset output directory
    if (os.path.exists(f"{OUTPUT_PATH}")):
        shutil.rmtree(f"{OUTPUT_PATH}")


def _create_outlines(topic: str):
    session_name = f"{topic} Outlines"
    ai_client = OpenAIMockService(session_name)

    # Create Outlines
    creator = OutlineCreator(topic, ai_client)
    outline_id = creator.create()

    return outline_id


def _create_page_material(topic: str):
    session_name = f"{topic} Page Material"
    ai_client = OpenAIMockService(session_name)

    creator = PageMaterialCreator(topic, ai_client)
    outline = creator.create_pages_from_outline()

    return outline


def _create_practice_skill_challenges(topic: str):
    session_name = f"{topic} Practice Skill Challenge"
    ai_client = OpenAIMockService(session_name)

    creator = PracticeSkillChallengeCreator(topic, ai_client)
    outline = creator.create_practice_skill_challenges()

    return outline


def _create_final_skill_challenges(topic: str):
    session_name = f"{topic} Final Skill Challenge"
    ai_client = OpenAIMockService(session_name)

    creator = FinalSkillChallengeCreator(topic, ai_client)
    outline = creator.create_final_skill_challenges()

    return outline



def test_create_full_course():
    _setup_test()

    slug = 'ruby-on-rails'
    topic = 'Ruby on Rails'

    # Begin creating course outlines
    outline_id = _create_outlines(topic)
    
    # Checking output
    assert outline_id == 1

    # Begin creating page material
    outline_rows = _create_page_material(topic)

    # Checking output
    for row in outline_rows:
        if row['type'] == 'page':
            page_record = DB.query(Page).filter(
                Page.course_slug == row['courseSlug'],
                Page.chapter_slug == row['chapterSlug'],
                Page.slug == row['slug']
            ).first()

            assert page_record != None
            assert page_record.content != None
            assert page_record.generated == True


    # Begin creating practice skill challenges
    outline_rows = _create_practice_skill_challenges(topic)

    # Checking output
    for row in outline_rows:
        if row['type'] == 'challenge':
            page_record = DB.query(Page).filter(
                Page.course_slug == row['courseSlug'],
                Page.chapter_slug == row['chapterSlug'],
                Page.slug == row['slug']
            ).first()

            assert page_record != None
            assert page_record.content != None
            assert page_record.generated == True


    # Begin creating final skill challenges
    outline_rows = _create_final_skill_challenges(topic)

    # Checking output
    for row in outline_rows:
        if row['type'] == 'final-skill-challenge':
            page_record = DB.query(Page).filter(
                Page.course_slug == row['courseSlug'],
                Page.chapter_slug == row['chapterSlug'],
                Page.slug == row['slug']
            ).first()

            assert page_record != None
            assert page_record.content != None
            assert page_record.generated == True

