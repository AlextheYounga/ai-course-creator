import shutil
import os
from ..mocks.openai_mock_service import OpenAIMockService
from ..mocks.db import *
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator


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
    outline = creator.create_from_outline()

    return outline


def _create_practice_skill_challenges(topic: str):
    session_name = f"{topic} Practice Skill Challenge"
    ai_client = OpenAIMockService(session_name)

    creator = PracticeSkillChallengeCreator(topic, ai_client)
    outline = creator.create_from_outline()

    return outline


def _create_final_skill_challenges(topic: str):
    session_name = f"{topic} Final Skill Challenge"
    ai_client = OpenAIMockService(session_name)

    creator = FinalSkillChallengeCreator(topic, ai_client)
    outline = creator.create_from_outline()

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
    pages = _create_page_material(topic)

    # Checking output
    for page in pages:
        if page.type == 'page':
            assert page != None
            assert page.content != None
            assert page.generated == True

    # Begin creating practice skill challenges
    practice_pages = _create_practice_skill_challenges(topic)

    # Checking output
    for page in practice_pages:
        if page.type == 'challenge':
            assert page != None
            assert page.content != None
            assert page.generated == True

    # Begin creating final skill challenges
    fsc_pages = _create_final_skill_challenges(topic)

    # Checking output
    for page in fsc_pages:
        assert page != None
        assert page.content != None
        assert page.generated == True

