from src.utils.shortcode import Shortcode
import re
import markdown
from bs4 import BeautifulSoup



class MapCodeEditorFieldsToNodeHandler:
    def __init__(self, data: dict):
        self.data = data
        self.shortcode_data = data['shortcode']

    def handle(self):
        parsed_content, nested_fields = self._parse_and_replace_nested_fields_from_shortcode_content()
        editor_data = self._parse_editor_data_from_content(parsed_content)

        code_editor_fields = {
            'name': nested_fields.get('name', None),
            'question': nested_fields.get('question', None),
            'answer': nested_fields.get('answer', None),
            'expectedOutput': nested_fields.get('expectedOutput', None),
            'exampleAnswer': nested_fields.get('exampleAnswer', None),
            'mustContain': nested_fields.get('mustContain', None),
            'content': editor_data.get('content', None),
            'language': editor_data.get('language', None)
        }

        return code_editor_fields



    def _parse_and_replace_nested_fields_from_shortcode_content(self):
        nested_fields = {
            'name': '',
            'question': '',
            'answer': '',
            'expectedOutput': '',
            'exampleAnswer': '',
            'mustContain': []
        }

        content = self.shortcode_data['shortcode']['content']

        for field in list(nested_fields.keys()):
            if isinstance(nested_fields[field], list):
                matches = re.finditer(Shortcode.shortcode_regex(field), content)
                if not matches: continue

                for match in matches:
                    value = Shortcode.from_match(match).get('content', None)
                    if value:
                        nested_fields[field].append(value.strip())
                        content = content.replace(match.group(), '')

            else:
                match = Shortcode.shortcode_regex(field).search(content)
                if not match: continue
                value = Shortcode.from_match(match).get('content', None)

                if value:
                    nested_fields[field] = value.strip()
                    content = content.replace(match.group(), '')

        nested_fields = {k: v for k, v in nested_fields.items() if len(v) > 0}

        return content, nested_fields


    def _parse_editor_data_from_content(self, parsed_content: str):
        html = markdown.markdown(parsed_content, extensions=['fenced_code'])
        soup = BeautifulSoup(html, 'html.parser')

        code_block = soup.find('code')
        language = self._parse_language(code_block)

        editor_data = {
            'content': code_block.getText() if code_block else None,
            'language': language
        }

        return editor_data


    def _parse_language(self, code_block: BeautifulSoup):
        language = None
        code_block_class_list = code_block.get('class') if code_block else None

        for clss in code_block_class_list:
            if 'language-' in clss:
                language = clss.split('language-')[1]
                break

        return language
