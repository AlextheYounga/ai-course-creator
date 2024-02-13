from .mocks.db import *
from src.mapping.node_parser import NodeParser

PAGE_CONTENT = open('test/fixtures/responses/page.md').read()



def _setup_test():
    truncate_tables()
    topic = Topic.first_or_create(DB, name="Ruby on Rails")
    page_record = Page.first_or_create(
        DB,
        topic,
        {
            'name': "Test Page",
            'outlineName': "series-1",
            'courseSlug': "test-course",
            'chapterSlug': "test-chapter",
            'position': 0,
            'positionInCourse': 0,
            'content': PAGE_CONTENT,
        })
    return page_record


def test_parse_content():
    page_record = _setup_test()
    page = NodeParser.parse_nodes(page_record)

    assert page.nodes != None
    assert len(page.nodes) == 3
