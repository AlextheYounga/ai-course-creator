from ..mocks.mock_db import *
from app.server.controllers.page_controller import PageController


def _setup_test():
    truncate_tables()
    import_sql_from_file(DB_PATH, 'test/fixtures/full-outline-interactives.sql.zip', zipped=True)


def test_get_full_page_html():
    _setup_test()

    page = PageController.get_page(1)

    assert page['id'] == 1
    assert len(page['interactives']) > 0
    assert page['content'] is not None
