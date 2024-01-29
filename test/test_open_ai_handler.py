import os
import shutil
from test.mocks.openai_mock_service import OpenAIMockService


LOG_PATH = "test/out/logs"


def _setup_test():
    if (os.path.exists(LOG_PATH)):
        shutil.rmtree(LOG_PATH)

    os.makedirs(LOG_PATH)
    open(f"{LOG_PATH}/chat.log", 'w').close()



def test_open_ai_handler_bad_response():
    _setup_test()

    mock_response = open('test/fixtures/responses/bad-yaml-response.md').read()

    open_ai_handler = OpenAIMockService("test", mock_response)
    validated_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})
    parsed_yaml = validated_response['dict']
    assert len(parsed_yaml) == 2
    assert open_ai_handler.retry_count == 0


def test_open_ai_handler_bad_response_scenario_2():
    _setup_test()

    mock_response = open('test/fixtures/responses/bad-yaml-response-2.md').read()

    open_ai_handler = OpenAIMockService("test", mock_response)
    validated_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})
    parsed_yaml = validated_response['dict']
    assert len(parsed_yaml) == 10
    assert open_ai_handler.retry_count == 0


def test_open_ai_handler_bad_response_scenario_3():
    _setup_test()

    mock_response = open('test/fixtures/responses/bad-yaml-response-3.md').read()

    open_ai_handler = OpenAIMockService("test", mock_response)
    validated_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})
    parsed_yaml = validated_response['dict']
    assert len(parsed_yaml) == 2
    assert open_ai_handler.retry_count == 0


def test_open_ai_handler_hopeless_response():
    _setup_test()

    mock_response = open('test/fixtures/responses/hopeless-yaml-response.md').read()

    open_ai_handler = OpenAIMockService("test", mock_response)
    hopeless_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})
    assert hopeless_response['valid'] == False
    assert open_ai_handler.retry_count == 3


def test_open_ai_handler_good_response():
    _setup_test()

    mock_response = open('test/fixtures/responses/good-yaml-response.md').read()

    open_ai_handler = OpenAIMockService("test", mock_response)
    good_response = open_ai_handler.send_prompt("test", [], {'yamlExpected': True})

    assert good_response['valid'] == True
    assert len(good_response['dict']) == 2
    assert isinstance(good_response['yaml'], str)
    assert "```" not in good_response['yaml']
