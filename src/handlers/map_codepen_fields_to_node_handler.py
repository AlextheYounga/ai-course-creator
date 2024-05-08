from src.utils.shortcode import Shortcode
import re
import markdown
from bs4 import BeautifulSoup



class MapCodepenFieldsToNodeHandler:
    def __init__(self, data: dict):
        self.data = data
        self.shortcode_data = data['shortcode']

    def handle(self):
        nested_fields = self._parse_simple_nested_fields_from_shortcode_content()
        codepen_content = self._parse_nested_code_fields()

        code_editor_fields = {
            'name': nested_fields.get('name', None),
            'description': nested_fields.get('description', None),
            'dependencies': nested_fields.get('dependencies', None),
            'content': codepen_content,
        }

        return code_editor_fields


    def _parse_simple_nested_fields_from_shortcode_content(self):
        nested_fields = {
            'name': '',
            'description': '',
            'dependencies': [],
        }

        content = self.shortcode_data['shortcode']['content']

        for field in list(nested_fields.keys()):
            # If field is a list
            if isinstance(nested_fields[field], list):
                matches = re.finditer(Shortcode.shortcode_regex(field), content)
                if not matches: continue

                for match in matches:
                    value = Shortcode.from_match(match).get('content', None)
                    if value:
                        nested_fields[field].append(value.strip())

            # If field is a string
            else:
                match = Shortcode.shortcode_regex(field).search(content)
                if not match: continue
                inner_content = Shortcode.from_match(match).get('content', None)

                if inner_content:
                    nested_fields[field] = inner_content


        nested_fields = {k: v for k, v in nested_fields.items() if len(v) > 0}

        return nested_fields


    def _parse_nested_code_fields(self):
        content = self.shortcode_data['shortcode']['content']
        code = {
            'template': {},
            'styles': {},
            'scripts': {},
        }

        for field in list(code.keys()):
            match = Shortcode.shortcode_regex(field).search(content)
            if not match: continue

            inner_content = Shortcode.from_match(match).get('content', None)

            html = markdown.markdown(inner_content, extensions=['fenced_code'])
            soup = BeautifulSoup(html, 'html.parser')

            code_block = soup.find('code')

            code[field] = {
                'language': self._parse_language(code_block),
                'content': code_block.get_text()
            }

        return code


    def _parse_language(self, code_block: BeautifulSoup):
        language = None
        code_block_class_list = code_block.get('class') if code_block else None

        for clss in code_block_class_list:
            if 'language-' in clss:
                language = clss.split('language-')[1]
                break

        return language
