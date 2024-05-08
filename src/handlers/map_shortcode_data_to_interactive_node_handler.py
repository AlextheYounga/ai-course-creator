from db.db import DB, Topic
from src.utils.shortcode import Shortcode
from .map_codepen_fields_to_node_handler import MapCodepenFieldsToNodeHandler
from .map_multiple_choice_fields_to_node_handler import MapMultipleChoiceFieldsToNodeHandler
from .map_code_editor_fields_to_node_handler import MapCodeEditorFieldsToNodeHandler
from cuid import cuid



class MapShortcodeDataToInteractiveNodeHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.shortcode_data = data['shortcode']
        self.topic = self.db.get(Topic, data['topicId'])
        self.tag = self.shortcode_data['shortcode']['tag']


    def handle(self):
        nested_fields = self._parse_nested_fields_from_shortcode_content()
        shortcode_attrs = self.shortcode_data['shortcode']['attrs']
        named_attrs = shortcode_attrs.get('named', {}) if isinstance(shortcode_attrs, dict) else {}
        custom_fields = self._parse_custom_fields()

        interactive_node = {
            'id': named_attrs.get('id', cuid()),
            'name': nested_fields.get('name', None),
            'question': nested_fields.get('question', None),
            'answer': nested_fields.get('answer', None),
            'content': nested_fields.get('content', None),
            'type': self.tag,
            'language': named_attrs.get('language', None),
            'expectedOutput': nested_fields.get('expectedOutput', None),
            'exampleAnswer': nested_fields.get('exampleAnswer', None),
            'hint': nested_fields.get('hint', None),
            'readOnly': self._convert_bool(named_attrs.get('readOnly', None)),
            'submittable': self._convert_bool(named_attrs.get('submittable', None)),
            'mustContain': named_attrs.get('mustContain', None),
            'index': self.shortcode_data['index'],
            'shortcode': self.shortcode_data['match']
        }

        interactive_node.update(custom_fields)

        return self._remove_none_attributes(interactive_node)


    def _parse_custom_fields(self):
        custom_fields = {}

        if self.tag in ['multipleChoice', 'trueFalse']:
            custom_fields = MapMultipleChoiceFieldsToNodeHandler(self.data).handle()

        if self.tag in ['codeEditor', 'codeSnippet']:
            custom_fields = MapCodeEditorFieldsToNodeHandler(self.data).handle()

        if self.tag == 'codepen':
            custom_fields = MapCodepenFieldsToNodeHandler(self.data).handle()

        return custom_fields


    def _parse_nested_fields_from_shortcode_content(self):
        nested_fields = {
            'question': None,
            'hint': None,
            'mustContain': None,
            'answer': None,
            'name': None,
            'content': None
        }

        for field in list(nested_fields.keys()):
            content = self.shortcode_data['shortcode']['content']
            match = Shortcode.shortcode_regex(field).search(content)
            if not match: continue

            value = Shortcode.from_match(match).get('content', None)
            nested_fields[field] = value.strip() if value else None

        return self._remove_none_attributes(nested_fields)


    def _convert_bool(self, value):
        if value == None: return None
        if isinstance(value, bool): return value
        return value.strip().lower() in ['true', '1', 'yes']


    def _remove_none_attributes(self, data):
        return {k: v for k, v in data.items() if v is not None}
