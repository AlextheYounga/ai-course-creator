from src.utils.shortcode import Shortcode
import markdown
from bs4 import BeautifulSoup



class MapMultipleChoiceFieldsToNodeHandler:
    def __init__(self, data: dict):
        self.data = data
        self.shortcode_data = data['shortcode']

    def handle(self):
        parsed_content, nested_fields = self._parse_and_replace_nested_fields_from_shortcode_content()
        choices, answer = self._parse_content_for_answer_choices(parsed_content)

        multiple_choice_fields = {
            'name': nested_fields.get('name', None),
            'question': nested_fields.get('question', None),
            'answer': answer,
            'content': choices,
        }

        return multiple_choice_fields


    def _parse_and_replace_nested_fields_from_shortcode_content(self):
        nested_fields = {
            'question': None,
            'name': None,
        }

        content = self.shortcode_data['shortcode']['content']

        for field in list(nested_fields.keys()):
            match = Shortcode.shortcode_regex(field).search(content)
            if not match: continue

            nested_fields[field] = Shortcode.from_match(match).get('content', None)
            content = content.replace(match.group(), '')

        nested_fields = self._remove_none_attributes(nested_fields)

        return content, nested_fields


    def _parse_content_for_answer_choices(self, parsed_content: str):
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


    def _remove_none_attributes(self, data):
        return {k: v for k, v in data.items() if v is not None}
