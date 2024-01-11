import markdown
from bs4 import BeautifulSoup


EXPECTED_COURSE_OUTLINE_RESPONSE = open('test/fixtures/responses/course-outline.md').read()
EXPECTED_DRAFT_OUTLINE_RESPONSE = open('test/fixtures/responses/draft-outline.md').read()
EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_PAGE_RESPONSE = open('test/fixtures/responses/page.md').read()
EXPECTED_PRACTICE_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/practice-skill-challenge.md').read()
EXPECTED_FINAL_SKILL_CHALLENGE_RESPONSE = open('test/fixtures/responses/final-skill-challenge.md').read()


class OpenAIMockService:
    def __init__(self, session_name: str):
        # Initialize logger
        self.session_name = session_name
        self.yaml_expected = False

    def send_prompt(self, name: str, messages: list[dict], options: dict = {}):
        self.yaml_expected = options.get('yamlExpected', False)

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
            return self.build_mock_response(EXPECTED_FINAL_SKILL_CHALLENGE_RESPONSE)
        else:
            return None


    def parse_yaml(self, content: str):
        html = markdown.markdown(content, extensions=['fenced_code'])
        soup = BeautifulSoup(html, 'html.parser')
        code_block = soup.find('code')
        yaml_content = code_block.get_text()

        return yaml_content


    def build_mock_response(self, content: str):
        parsed_yaml = self.parse_yaml(content) if self.yaml_expected else None

        validate_response = {
            'valid': True,
            'content': content,
            'yaml': parsed_yaml
        }

        return validate_response
