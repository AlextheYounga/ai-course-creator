from unittest.mock import MagicMock


EXPECTED_COURSE_OUTLINE_RESPONSE = open('test/fixtures/responses/course-outline.md').read()
EXPECTED_DRAFT_OUTLINE_RESPONSE = open('test/fixtures/responses/draft-outline.md').read()
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_PAGE_RESPONSE = open('test/fixtures/responses/page.md').read()
EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/practice-skill-challenge.md').read()


class OpenAIMockService:
    def __init__(self, session_name: str):
        # Initialize logger
        self.session_name = session_name

    def build_mock_response(self, content: str):
        mock_api = MagicMock()
        mock_api.completion.choices[0].message.content = content
        return mock_api.completion

    def send_prompt(self, name: str, _messages: list[dict], _quiet: bool = False) -> MagicMock:
        if name == 'skills':
            return self.build_mock_response(EXPECTED_SKILLS_RESPONSE)
        elif name == 'draft-outline':
            return self.build_mock_response(EXPECTED_DRAFT_OUTLINE_RESPONSE)
        elif name == 'optimize-outline':
            return self.build_mock_response(EXPECTED_COURSE_OUTLINE_RESPONSE)
        elif name == 'page-material':
            return self.build_mock_response(EXPECTED_PAGE_RESPONSE)
        elif name == 'practice-skill-challenge':
            return self.build_mock_response(EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE)
        elif name == 'final-skill-challenge':
            return self.build_mock_response(EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE)
        else:
            return None
