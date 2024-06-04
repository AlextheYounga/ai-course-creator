from functools import lru_cache
import re
import markdown
from bs4 import BeautifulSoup
from db.db import DB, Response, OutlineEntity, Page, Interactive
from src.utils.shortcode import Shortcode
from src.events.events import CodeEditorInteractiveSavedFromResponse, CodeEditorInteractiveShortcodeParsingFailed


class ProcessCodeEditorInteractivesResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'codeEditor'


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
            'answerType': named_attrs.get('answerType', None),
            'difficulty': named_attrs.get('difficulty', None),
            'content': nested_fields.get('editorData', None),
            'expectedOutput': nested_fields.get('expectedOutput', None),
            'exampleAnswer': nested_fields.get('exampleAnswer', None),
            'testCase': nested_fields.get('testCase', None),
            'mustContain': nested_fields.get('mustContain', None),
            'language': nested_fields.get('language', None),
            "hint": nested_fields.get('hint', None),
            'shortcode': shortcode['match'],
            'index': shortcode['index'],
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
        # This function can automatically parse nested fields from a shortcode block
        # If there are multiple of the same shortcodes, it will return as a list
        parsed_fields = {}
        nested_fields = {
            'simple': [
                'name',
                'question',
                'answer',
                'description',
            ],
            'list': [
                'mustContain',
            ],
            'code': [
                'editorData',
                'expectedOutput',
                'exampleAnswer',
                'testCase',
            ]

        }

        content = shortcode['shortcode']['content']

        for field_type in nested_fields:
            for field in nested_fields[field_type]:
                # Search results is returned in a generator; so we need to loop through it.
                # We'll store the parsed values in a list and take the first value if there's only one.

                parsed_values = []
                search_results = self._search_for_shortcode_tags(field, content)
                if not search_results: continue

                match field_type:
                    case 'simple':  # Normal string values
                        for block in search_results:
                            block_content = Shortcode.from_match(block).get('content', None)
                            if not block_content: continue

                            parsed_values.append(block_content.strip())

                        if not parsed_values: continue
                        if len(parsed_values) == 1:
                            parsed_fields[field] = parsed_values[0]  # If only one block, return as string
                        else:
                            parsed_fields[field] = parsed_values  # If multiple values, return as list
                    case 'list':
                        for block in search_results:
                            block_content = Shortcode.from_match(block).get('content', None)
                            if not block_content: continue

                            parsed_values.append(block_content.strip())

                        if not parsed_values: continue
                        parsed_fields[field] = parsed_values  # If multiple values, return as list
                    case 'code':
                        for block in search_results:
                            block_content = Shortcode.from_match(block).get('content', None)
                            if not block_content: continue

                            # Check if content is wrapped in code block
                            if '```' in block_content:
                                code_block = self._parse_code_block(block_content)
                                if not code_block: continue

                                # We can only get the language field from a code block
                                if not parsed_fields.get('language', False):
                                    parsed_fields['language'] = code_block['language']

                                parsed_values.append(code_block['content'])
                            else:
                                parsed_values.append(block_content.strip())  # Normal string values

                        if not parsed_values: continue
                        if len(parsed_values) == 1:
                            parsed_fields[field] = parsed_values[0]  # If only one block, return as string
                        else:
                            parsed_fields[field] = parsed_values  # If multiple values, return as list

        return parsed_fields


    def _parse_code_block(self, content):
        code_content_markdown = content.strip()
        html = markdown.markdown(code_content_markdown, extensions=['fenced_code'])
        soup = BeautifulSoup(html, 'html.parser')
        code_block = soup.find('code')

        language = self._parse_language(code_block)
        code_content = code_block.getText() if code_block else None

        return {
            'content': code_content,
            'language': language
        }


    def _parse_language(self, code_block: BeautifulSoup):
        language = None
        code_block_class_list = code_block.get('class') if code_block else None

        for clss in code_block_class_list:
            if 'language-' in clss:
                language = clss.split('language-')[1]
                break

        return language


    def _search_for_shortcode_tags(self, tag, content):
        match_blocks = re.finditer(Shortcode.shortcode_regex(tag), content)
        if not match_blocks: return None
        return match_blocks


    @ lru_cache(maxsize=None)  # memoize
    def _get_page_outline_entity_id(self):
        # Get interactive relation to outline entity
        return self.db.query(OutlineEntity.id).filter(
            OutlineEntity.entity_id == self.page.id,
            OutlineEntity.entity_type == 'Page',
            OutlineEntity.outline_id == self.data['outlineId']
        ).first()[0]  # returns as tuple


    def _remove_none_attributes(self, data):
        return {k: v for k, v in data.items() if v is not None}
