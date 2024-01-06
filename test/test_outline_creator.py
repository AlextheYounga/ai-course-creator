import json
from src.openai.outline_creator import OutlineCreator 

EXPECTED_SKILLS_RESPONSE = open('test/fixtures/responses/skills.md').read()
EXPECTED_SERIES_RESPONSE = open('test/fixtures/responses/series.md').read()

creator = OutlineCreator("Ruby on Rails")
skills_json = creator.handle_topics_response(EXPECTED_SKILLS_RESPONSE)
series_json = creator.handle_series_response(EXPECTED_SERIES_RESPONSE)


def test_parse_skills_response():
    creator = OutlineCreator("Ruby on Rails")
    json_list = creator.handle_topics_response(EXPECTED_SKILLS_RESPONSE)

    assert len(json_list) == 16
    
    for item in json_list:
        assert item['header'] is not None
        assert len(item['children']) == 3


def test_parse_series_response():
    creator = OutlineCreator("Ruby on Rails")
    json_list = creator.handle_series_response(EXPECTED_SERIES_RESPONSE)

    assert len(json_list) == 8
    
    for course in json_list:
        assert course['courseName'] is not None
        assert len(course['modules']) == 2

        for module in course['modules']:
            assert module['name'] is not None
            assert len(module['skills']) > 0


def test_parse_series_response():
    creator = OutlineCreator("Ruby on Rails")
    json_list = creator.handle_series_response(EXPECTED_SERIES_RESPONSE)

    assert len(json_list) == 8
    
    for course in json_list:
        assert course['courseName'] is not None
        assert len(course['modules']) == 2

        for module in course['modules']:
            assert module['name'] is not None
            assert len(module['skills']) > 0