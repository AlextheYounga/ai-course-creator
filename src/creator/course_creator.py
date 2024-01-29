from src.llm.openai_handler import OpenAiHandler
from src.creator.outlines.outline_creator import OutlineCreator
from src.creator.outlines.outline_processor import OutlineProcessor
from src.creator.challenges.practice_skill_challenge_creator import PracticeSkillChallengeCreator
from src.creator.challenges.final_skill_challenge_creator import FinalSkillChallengeCreator
from src.creator.pages.page_material_creator import PageMaterialCreator


class CourseCreator:
    @staticmethod
    def dump_outline_content(outline_id: int):
        return OutlineProcessor.dump_pages_from_outline(outline_id)


    @staticmethod
    def create_outlines(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Outlines"
            ai_client = OpenAiHandler(session_name)

            creator = OutlineCreator(topic, ai_client)
            outline_id = creator.create()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def create_page_material(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Page Material"
            ai_client = OpenAiHandler(session_name)

            creator = PageMaterialCreator(topic, ai_client)
            outline_id = creator.create_from_outline()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def create_practice_skill_challenges(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Practice Skill Challenges"
            ai_client = OpenAiHandler(session_name)

            creator = PracticeSkillChallengeCreator(topic, ai_client)
            outline_id = creator.create_from_outline()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def create_final_skill_challenges(topics: list):
        outline_ids = []
        for topic in topics:
            session_name = f"{topic} Final Skill Challenges"
            ai_client = OpenAiHandler(session_name)

            creator = FinalSkillChallengeCreator(topic, ai_client)
            outline_id = creator.create_from_outline()

            outline_ids.append(outline_id)

        return outline_ids


    @staticmethod
    def run_all(topics: list):
        CourseCreator.create_outlines(topics)
        CourseCreator.create_page_material(topics)
        CourseCreator.create_practice_skill_challenges(topics)
        CourseCreator.create_final_skill_challenges(topics)
