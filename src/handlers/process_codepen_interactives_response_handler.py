from functools import lru_cache
import re
import markdown
from bs4 import BeautifulSoup
from src.utils.shortcode import Shortcode
from db.db import DB, Response, OutlineEntity, Page, Interactive
from src.events.events import CodepenInteractiveSavedFromResponse, CodepenInteractiveShortcodeParsingFailed


class ProcessCodepenInteractivesResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'codepen'


    def handle(self):
        interactive_ids = []
        content = self.response.content

        try:
            shortcodes = self._parse_shortcodes_from_content(content)

            for shortcode in shortcodes:
                interactive = self._map_shortcode_data_to_interactive(shortcode)

                # Save to Database
                self.db.add(interactive)
                self.db.commit()

                interactive_ids.append(interactive.id)

        except Exception as e:
            print(e)
            return CodepenInteractiveShortcodeParsingFailed({
                **self.data,
                'error': e.__class__.__name__,
                'errorMessage': e.__str__(),
                'content': content
            })

        return CodepenInteractiveSavedFromResponse({
            **self.data,
            'interactiveIds': interactive_ids
        })


    def _parse_shortcodes_from_content(self, content: str):
        shortcodes = []

        shortcode_matches = re.finditer(Shortcode.shortcode_regex(self.interactive_type), content)

        for match in shortcode_matches:
            shortcode = Shortcode.from_match_with_index(match)
            shortcode['match'] = match.group()
            shortcodes.append(shortcode)

        return shortcodes


    def _map_shortcode_data_to_interactive(self, shortcode):
        nested_fields = self._parse_nested_fields_from_shortcode(shortcode)
        shortcode_attrs = shortcode['shortcode']['attrs']
        named_attrs = shortcode_attrs.get('named', {}) if isinstance(shortcode_attrs, dict) else {}

        interactive_data = self._remove_none_attributes({
            'question': nested_fields.get('question', None),
            'answer': nested_fields.get('answer', None),
            'answerType': named_attrs.get('answerType', None),
            'content': nested_fields.get('content', None),
            'description': nested_fields.get('description', None),
            'dependencies': nested_fields.get('dependency', None),
            'shortcode': shortcode['match'],
            'index': shortcode['index'],
        })

        interactive = Interactive(
            page_source_id=self.page.id,
            type=self.interactive_type,
            data=interactive_data,
            meta={
                'responseId': self.response.id,
            },
        )

        return interactive


    def _parse_nested_fields_from_shortcode(self, shortcode):
        nested_fields = self._parse_simple_nested_fields_from_shortcode_content(shortcode)
        codepen_content = self._parse_codepen_specific_fields(shortcode)

        code_editor_fields = {
            'name': nested_fields.get('name', None),
            'description': nested_fields.get('description', None),
            'dependency': nested_fields.get('dependency', None),
            'content': codepen_content,
        }

        return code_editor_fields


    def _parse_simple_nested_fields_from_shortcode_content(self, shortcode):
        nested_fields = {
            'name': '',
            'description': '',
            'dependency': [],
        }

        content = shortcode['shortcode']['content']

        for field in list(nested_fields.keys()):
            match nested_fields[field].__class__.__name__:
                case 'list':
                    matches = re.finditer(Shortcode.shortcode_regex(field), content)
                    if not matches: continue

                    for match in matches:
                        value = Shortcode.from_match(match).get('content', None)
                        if value:
                            nested_fields[field].append(value.strip())

                case 'str':
                    match = Shortcode.shortcode_regex(field).search(content)
                    if not match: continue
                    inner_content = Shortcode.from_match(match).get('content', None)

                    if inner_content:
                        nested_fields[field] = inner_content

        nested_fields = {k: v for k, v in nested_fields.items() if len(v) > 0}

        return nested_fields


    def _parse_codepen_specific_fields(self, shortcode):
        content = shortcode['shortcode']['content']
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


    def _remove_none_attributes(self, data):
        return {k: v for k, v in data.items() if v is not None}
