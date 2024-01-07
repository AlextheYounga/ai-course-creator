import json
from src.openai.outlines.build_master_outline import MasterOutlineBuilder
from ..mocks.openai_mock_service import OpenAIMockService
from src.openai.outlines.generate_skills import SkillGenerator
from src.openai.outlines.draft_course_outline import OutlineDraft
from src.openai.outlines.build_master_outline import MasterOutlineBuilder

OUTPUT_PATH="test/out"
REPLACE_KEYS = ["{topic}", "{draft_outline}"]

# Sloppy happy path test
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
        draft_outline = draft.generate(skills['yaml'])

        # Finalize Outline
        builder = MasterOutlineBuilder(topic, ai_client, OUTPUT_PATH)
        master_outline = builder.generate(draft_outline['yaml'])

        course_list = [c['courseName'] for c in master_outline]
        assert len(course_list) == 15

# def test_create_outlines():
#     topics = ['Ruby on Rails']
#     for topic in topics:
#         session_name = f"{topic} Outlines"
#         ai_client = OpenAiHandler(session_name)

#         # Generate Skills
#         skill_generator = SkillGenerator(topic, ai_client)
#         skills_prompt = skill_generator.build_skills_prompt()

#         assert len(skills_prompt) == 2
        
#         completion = open('test/fixtures/responses/skills.md').read()
#         parsed_skills = skill_generator.handle_skills_response(completion)

#         # Generate Draft Outline
#         draft = OutlineDraft(topic, ai_client)
#         draft_prompt = draft.build_draft_prompt(parsed_skills['yaml'])

#         assert len(draft_prompt) == 2

#         completion = open('test/fixtures/responses/draft-outline.md').read()
#         draft_outline = draft.handle_outline_draft_response(completion)

#         # Finalize Outline
#         builder = MasterOutlineBuilder(topic, ai_client)
#         outline_data = draft_outline['dict']

#         master_outline = []
#         for course in draft_outline['dict']:
#             course_name = course['courseName']
#             modules = course['modules']

#             optimize_outline_prompt = builder.build_optimize_outline_prompt(course_name, outline_data, modules)

#             assert len(optimize_outline_prompt) == 2

#             completion = open('test/fixtures/responses/course-outline.md').read()
#             course_outline = builder.handle_course_optimize_response(completion)

#             course_object = {
#                 "courseName": course['courseName'],
#                 "chapters": course_outline['dict']
#             }

#             master_outline.append(course_object)

#         course_list = [c['courseName'] for c in master_outline]

#         assert len(course_list) == 15


