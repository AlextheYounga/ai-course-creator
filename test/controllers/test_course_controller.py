from ..mocks.mock_db import *
from app.server.controllers.course_controller import CourseController
import json
DB_PATH = 'test/data/test.db'


def _setup_test():
    truncate_tables()
    import_sql_data_from_file(DB_PATH, 'test/fixtures/full-outline-interactives.sql.zip', zipped=True)


def test_get_course_content():
    _setup_test()

    course = CourseController.get_course_content(1)

    assert course['id'] == 1
    assert len(course['chapters']) > 0
    assert len(course['pages']) > 0
