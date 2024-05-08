from db.db import DB, Page
import copy
import re
from src.utils.shortcode import Shortcode



class ParseShortcodesFromPageContentHandler:
    def __init__(self, data: dict):
        self.db = DB()
        self.page = self.db.get(Page, data['pageId'])

    def handle(self):
        shortcodes = []
        parsed_content = copy.copy(self.page.content)

        if self.page.content:
            interactive_types = ['codeEditor', 'multipleChoice', 'fillBlank', 'trueFalse', 'codepen']

            for tag in interactive_types:
                shortcode_matches = re.finditer(Shortcode.shortcode_regex(tag), self.page.content)

                for match in shortcode_matches:
                    shortcode = Shortcode.from_match_with_index(match)
                    shortcode['match'] = match.group()
                    shortcodes.append(shortcode)
                    parsed_content = parsed_content.replace(match.group(), '__SHORTCODE__')

        return shortcodes, parsed_content
