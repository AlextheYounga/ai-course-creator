from db.db import DB, Page, Topic
import markdown
from .parse_shortcodes_from_page_content_handler import ParseShortcodesFromPageContentHandler
from .map_shortcode_data_to_interactive_node_handler import MapShortcodeDataToInteractiveNodeHandler



class MapPageContentToNodesHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.page = self.db.get(Page, data['pageId'])
        self.topic = self.db.get(Topic, self.page.topic_id)
        self.settings = self._get_topic_settings()


    def handle(self):
        html_nodes = []
        interactive_nodes = []

        if self.page.content:
            shortcodes, parsed_content = ParseShortcodesFromPageContentHandler({'pageId': self.page.id}).handle()

            # Build HTML Nodes
            if (len(parsed_content) > 0) and ('__SHORTCODE__' in parsed_content):
                content_chunks = parsed_content.split('__SHORTCODE__')
                for content_chunk in content_chunks:
                    html_node = self._build_html_node(content_chunk, self.page.content)

                    if html_node: html_nodes.append(html_node)

            # Build Interactive Nodes
            for shortcode in shortcodes:
                interactive_node = MapShortcodeDataToInteractiveNodeHandler({
                    'shortcode': shortcode,
                    'topicId': self.page.topic_id
                }).handle()

                interactive_nodes.append(interactive_node)

        nodes = html_nodes + interactive_nodes
        nodes.sort(key=lambda x: x['index'])

        return nodes


    def _build_html_node(self, content_chunk: str, content: str) -> dict:
        # The markdown parser may get confused about shortcodes.
        # Just in case, we only run the parser on non-shortcode content, and we can concatenate them later.
        if content_chunk.strip() == '':
            return None

        html_element = markdown.markdown(content_chunk, extensions=['toc', 'fenced_code'])

        return {
            "content": html_element,
            "markdown": content_chunk,
            "type": "html",
            'index': content.index(content_chunk)
        }


    def _get_topic_settings(self):
        topic_settings = self.topic.get_settings('global')
        interactive_options = topic_settings.get('interactives', {})

        return {
            'codeEditors': interactive_options.get('codeEditor', True),
            'allCodeInEditors': topic_settings.get('allCodeInEditors', False)
        }
