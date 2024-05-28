from functools import lru_cache
import re
import markdown
from bs4 import BeautifulSoup
from db.db import DB, Response, OutlineEntity, Page, Interactive
from src.utils.shortcode import Shortcode
from src.events.events import MultipleChoiceInteractivesSavedFromResponse, MultipleChoiceInteractiveShortcodeParsingFailed


class ProcessMultipleChoiceInteractiveBatchResponseHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.response = self.db.get(Response, data['responseId'])
        self.page = self.db.get(Page, data['pageId'])
        self.interactive_type = 'multipleChoice'


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
            return MultipleChoiceInteractiveShortcodeParsingFailed({
                **self.data,
                'error': e.__class__.__name__,
                'errorMessage': e.__str__(),
                'content': content
            })

        return MultipleChoiceInteractivesSavedFromResponse({
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
            'description': nested_fields.get('description', None),
            'answerType': named_attrs.get('answerType', None),
            'difficulty': named_attrs.get('difficulty', None),
            'content': nested_fields.get('content', None),
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
        parsed_content, nested_fields = self._pop_nested_fields_from_shortcode_content(shortcode)
        choices, answer = self._parse_shortcode_for_markdown_answer_choices(parsed_content)

        multiple_choice_nested_fields = {
            'name': nested_fields.get('name', None),
            'question': nested_fields.get('question', None),
            'description': nested_fields.get('description', None),
            'answer': answer,
            'content': choices,
        }

        return multiple_choice_nested_fields


    def _pop_nested_fields_from_shortcode_content(self, shortcode):
        # We want to parse key nested fields first, and then we'll parse the content for the markdown answer choices.
        # Remember that the model sends us back some nested shortcode fields, but the answer choices are as a markdown checklist.
        nested_fields = {
            'question': None,
            'name': None,
            'description': None,
        }

        content = shortcode['shortcode']['content']

        for field in list(nested_fields.keys()):
            match = Shortcode.shortcode_regex(field).search(content)
            if not match: continue

            nested_fields[field] = Shortcode.from_match(match).get('content', None)
            content = content.replace(match.group(), '')

        return content, nested_fields


    def _parse_shortcode_for_markdown_answer_choices(self, parsed_content: str):
        choices = []
        answer = None
        html = markdown.markdown(parsed_content, extensions=['fenced_code', 'markdown_checklist.extension'])
        soup = BeautifulSoup(html, 'html.parser')
        checklist = soup.find('ul', {'class': 'checklist'})

        checklist_items = checklist.find_all('li') if checklist else []
        for item in checklist_items:
            checkbox = item.find('input')
            if not checkbox: continue

            value = item.getText().strip()

            if checkbox.has_attr('checked'):
                answer = value

            choices.append(value)

        return list(set(choices)), answer


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
