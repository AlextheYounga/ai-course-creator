from db.db import DB, Page, Interactive, Question, Answer
import re
import markdown
from bs4 import BeautifulSoup


class ContentParser:
    def __init__(self, page: Page):
        self.page = page


    def parse_multiple_choice_content(self, element: BeautifulSoup):
        choices_list = []
        choices = element.find(attrs={'id': 'choices'})

        for option in choices.find_all('option'):
            choices_list.append(option.text)

        return choices_list

    def parse_interactive(self, element: BeautifulSoup):
        question_element = element.find(attrs={'id': 'question'})
        answer_element = element.find(attrs={'id': 'correct-answer'})
        type = element.attrs['id'].split('answerable-')[1]

        question = Question.save(DB, question_element.text)
        answer = Answer.save(DB, question.id, answer_element.text)

        interactive_content = {
            'question': question.question,
            'answer': answer.value,
            'content': None
        }

        if type == 'multiple-choice':
            interactive_content['content'] = self.parse_multiple_choice_content(element)

        interactive = Interactive.save(DB, question.id, answer.id, type, interactive_content)

        return interactive


    def build_node(self, content_type: str, node):
        if content_type == "interactive":
            return {
                "id": node.id,
                "nodeType": content_type,
                "type": node.type,
                "content": node.content['content'],
                "question": node.content['question'],
                "answer": node.content['answer'],

            }
        if content_type == "html":
            return {
                "content": str(node),
                "nodeType": content_type
            }


    def parse_nodes(self):
        nodes = []
        if self.page.content:
            html = markdown.markdown(self.page.content, extensions=['fenced_code'])
            soup = BeautifulSoup(html, 'html.parser')

            html_node = BeautifulSoup('', 'html.parser')

            for element in soup.children:
                if type(element).__name__ == "Tag" and element.attrs.get('id', False) and 'answerable' in element.attrs['id']:
                    interactive = self.parse_interactive(element)
                    nodes.append(self.build_node("html", html_node))
                    nodes.append(self.build_node("interactive", interactive))
                    html_node = BeautifulSoup('', 'html.parser')
                    continue

                html_node.append(element)


            self.page.nodes = nodes
            DB.add(self.page)
            DB.commit()

        return self.page