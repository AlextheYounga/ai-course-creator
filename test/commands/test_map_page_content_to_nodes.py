from ..mocks.db import *
from src.commands.map_page_content_to_nodes import MapPageContentToNodes


OUTPUT_PATH = "test/out"
MASTER_OUTLINE = 'test/fixtures/master-outline.yaml'
DRAFTS_DB_PATH = 'test/data/drafts.db'
DB_PATH = 'test/data/test.db'


def _setup_test():
    # Reset output directory
    if (os.path.exists(f"{DRAFTS_DB_PATH}")):
        os.remove(f"{DRAFTS_DB_PATH}")

    truncate_tables()
    import_sql_data_from_file(DB_PATH, 'test/data/test.sql.zip', zipped=True)


def test_map_page_content_to_nodes():
    _setup_test()

    MapPageContentToNodes().run()

    pages = DB.query(Page).all()
    for page in pages:
        assert page.get_properties()['nodes'] is not None
