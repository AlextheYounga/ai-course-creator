from functools import lru_cache
import re
import markdown
from bs4 import BeautifulSoup
from db.db import DB, Response, OutlineEntity, Page, Interactive
from src.utils.shortcode import Shortcode
from src.events.events import CodeEditorInteractiveSavedFromResponse, CodeEditorInteractiveShortcodeParsingFailed


class ProcessCodeEditorInteractiveResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'codeEditor'


    def handle(self):
        interactive_ids = []
        completion = self.response.payload
        content = completion['choices'][0]['message']['content']

        try:
            shortcodes = self._parse_shortcodes_from_content(content)

            for shortcode in shortcodes:
                interactive = self._map_shortcode_data_to_interactive(shortcode)

                # Save to Database
                self.db.add(interactive)
                self.db.commit()

                interactive_ids.append(interactive.id)

        except Exception as e:
            return CodeEditorInteractiveShortcodeParsingFailed({
                **self.data,
                'error': e.__class__.__name__,
                'errorMessage': e.__str__(),
                'content': content
            })

        return CodeEditorInteractiveSavedFromResponse({
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
            'answer_type': named_attrs.get('answerType', None),
            'difficulty': named_attrs.get('difficulty', None),
            'content': nested_fields.get('content', None),
            'expectedOutput': nested_fields.get('expectedOutput', None),
            'exampleAnswer': nested_fields.get('exampleAnswer', None),
            'mustContain': nested_fields.get('mustContain', None),
            'language': nested_fields.get('language', None),
            "hint": nested_fields.get('hint', None),
            'shortcode': shortcode['match'],
            'shortcodeIndex': shortcode['index'],
        })

        interactive = Interactive(
            outline_entity_id=self._get_page_outline_entity_id(),
            type=self.interactive_type,
            data=interactive_data,
            meta={
                'pageId': self.page.id,
                'responseId': self.response.id,
            },
        )

        return interactive


    def _parse_nested_fields_from_shortcode(self, shortcode):
        nested_fields, parsed_content = self._pop_nested_fields_from_shortcode_content(shortcode)
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


    def _pop_nested_fields_from_shortcode_content(self, shortcode):
        nested_fields = {
            'name': '',
            'question': '',
            'answer': '',
            'expectedOutput': '',
            'exampleAnswer': '',
            'mustContain': []
        }

        content = shortcode['shortcode']['content']

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

        return nested_fields, content


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


    @lru_cache(maxsize=None)  # memoize
    def _get_page_outline_entity_id(self):
        # Get interactive relation to outline entity
        return self.db.query(OutlineEntity.id).filter(
            OutlineEntity.entity_id == self.page.id,
            OutlineEntity.entity_type == 'Page',
            OutlineEntity.outline_id == self.data['outlineId']
        ).first()[0]  # returns as tuple


    def _remove_none_attributes(self, data):
        return {k: v for k, v in data.items() if v is not None}
