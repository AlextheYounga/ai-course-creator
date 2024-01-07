import shutil
import os
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from ..mocks.openai_mock_service import OpenAIMockService
from src.openai.outlines.generate_skills import SkillGenerator
from src.openai.outlines.draft_course_outline import OutlineDraft
from src.openai.outlines.build_master_outline import MasterOutlineBuilder

OUTPUT_PATH = "test/out"

# Reset output directory
slug = 'ruby-on-rails'
if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
    shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

# Semi decent happy path test
def test_create_outlines():
    topics = ['Ruby on Rails']
    for topic in topics:
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

        course_list = [c['courseName'] for c in master_outline]
        assert len(course_list) == 15
