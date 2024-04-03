from db.db import DB, Page
from ...utils.shortcode import Shortcode
from bs4 import BeautifulSoup
import copy
import re

CONTROL_TYPE_MAPPING = {
    'multiple-choice': 'multipleChoice',
    'true-false': 'multipleChoice',
    'code-editor': 'codeEditor',
    'fill-blank': 'fillInTheBlank',
    'html': 'html'
}


class BackfillPageContentWithShortcodes:
    def run(self):
        pages = DB.query(Page).all()

        for page in pages:
            page_content = copy.copy(page.content)

            if page.content:
                soup = BeautifulSoup(page.content, 'html.parser')
                answerable_elements = soup.findAll("div", {"id": re.compile('answerable-*')})
                if len(answerable_elements) == 0: continue

                for element in answerable_elements:
                    try:
                        interactive_content = self._parse_interactive(element)
                    except ValueError as e:
                        print(f"Error parsing interactive content: {e}")
                        continue

                    interactive_node = interactive_node = self._build_interactive_node(interactive_content)

                    if interactive_node:
                        shortcode_data = {
                            'tag': interactive_node['type'],
                            'attrs': {'named': self._build_attributes(interactive_node)},
                            'content': self._build_nested_shortcodes(interactive_node)
                        }

                        if interactive_node['type'] == 'multipleChoice':
                            shortcode_data['content'] += self._build_multiple_choice_markdown_choices(
                                interactive_node['content'],
                                interactive_node['answer']
                            )

                        if interactive_node['type'] == 'codeEditor':
                            shortcode_data['content'] += self._build_code_editor_data(element, interactive_node)

                        shortcode = Shortcode.shortcode_string(shortcode_data)
                        element.replace_with(shortcode)
                        page_content = str(soup)

                        page.content = page_content
                        DB.commit()

                        print(f"Updated page {page.id} with shortcodes.")


    def _parse_interactive(self, element: BeautifulSoup):
        question_element = element.find(attrs={'id': 'question'})
        answer_element = element.find(attrs={'id': 'correct-answer'})
        type = element.attrs['id'].split('answerable-')[1]

        if question_element is None:
            raise ValueError(f"{type} question is missing.")
        if answer_element is None:
            raise ValueError(f"{type} question has no identified correct answer.")

        interactive_content = {
            'question': question_element.text,
            'answer': answer_element.text,
            'content': None,
            'type': CONTROL_TYPE_MAPPING[type]
        }

        if type == 'multiple-choice' or type == 'true-false':
            interactive_content['content'] = self._parse_multiple_choice_content(element)
        if type == 'code-editor':
            interactive_content['content'] = element.text
            interactive_content['language'] = self._parse_language(element)
            interactive_content['submittable'] = True

        return interactive_content


    def _build_interactive_node(self, node: dict) -> dict:
        interactive_node = {
            "type": node['type'],
            "content": node.get('content', None),
            "question": node.get('question', None),
            "answer": node.get('answer', None),
            "submittable": node.get('submittable', True),
            "language": node.get('language', None),
            "readOnly": node.get('readOnly', False),
            "mustContain": node.get('mustContain', []),
            "editorData": node.get('editorData', None),
            "hint": node.get('hint', None),
        }

        # Remove any None values
        interactive_node = {k: v for k, v in interactive_node.items() if v != None}

        return interactive_node



    def _parse_multiple_choice_content(self, element: BeautifulSoup) -> list:
        choices_list = []
        choices = element.find(attrs={'id': 'choices'})

        for option in choices.find_all('option'):
            choices_list.append(option.text)

        return list(set(choices_list))


    def _parse_language(self, element: BeautifulSoup) -> str:
        language = 'plaintext'
        code = element.find('code')
        if code:
            code_class = code.attrs.get('class', [])
            contains_language = True in ['lang' in clss for clss in code_class]

            if contains_language:
                language = code_class[0].split('-')[1]
                if language: return language

        return language


    def _build_attributes(self, interactive_node: dict):
        omit_fields = ['question', 'answer', 'mustContain', 'hint', 'content', 'type']
        attributes = {}

        for key, value in interactive_node.items():
            if value is not None and key not in omit_fields:
                attributes[key] = value

        return attributes


    def _build_nested_shortcodes(self, interactive_node: dict):
        shortcodes = []
        nested_fields = ['question', 'answer', 'mustContain', 'hint', 'content']

        for field in nested_fields:
            if field == 'content' and interactive_node['type'] in ['multipleChoice', 'codeEditor']: continue

            if interactive_node.get(field, False):
                if isinstance(interactive_node[field], list):
                    for item in interactive_node[field]:
                        shortcode = Shortcode.shortcode_string({
                            'tag': field,
                            'content': item,
                        })

                        shortcodes.append(shortcode)
                else:
                    shortcode = Shortcode.shortcode_string({
                        'tag': field,
                        'content': interactive_node[field],
                    })

                    shortcodes.append(shortcode)

        return '\n'.join(shortcodes)


    def _build_multiple_choice_markdown_choices(self, content, answer):
        markdown = '\n\n'
        for choice in content:
            if choice == answer:
                markdown += f'- [x] {choice}\n'
                continue

            markdown += f'- [ ] {choice}\n'

        return markdown + '\n'


    def _build_code_editor_data(self, element, interactive_node):
        language = interactive_node['language']
        code = element.find('code').text

        return f"\n\n```{language}\n{code}\n```\n\n"
