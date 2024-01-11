import shutil
import os
from src.openai.page_material_creator import PageMaterialCreator
from .mocks.openai_mock_service import OpenAIMockService

# What the outline looks like before we run page material creator
PATHLESS_MASTER_OUTLINE = 'test/fixtures/data/master-outline-1.json'
OUTPUT_PATH = "test/out/course_material"


# Setup paths
def setup_test():
    slug = 'ruby-on-rails'
    if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
        shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

    os.makedirs(f"{OUTPUT_PATH}/{slug}", exist_ok=True)
    shutil.copy(PATHLESS_MASTER_OUTLINE, f"{OUTPUT_PATH}/{slug}/master-outline.json")



def test_create_page_material():
    # Semi decent happy path test
    setup_test()

    slug = 'ruby-on-rails'
    topics = ['Ruby on Rails']
    for topic in topics:

        session_name = f"{topic} Page Material"
        ai_client = OpenAIMockService(session_name)

        creator = PageMaterialCreator(topic, ai_client, OUTPUT_PATH)
        outline = creator.create_pages_from_outline()

        assert len(os.listdir(f"{OUTPUT_PATH}/{slug}/content")) == 7

        for course_slug, course_data in outline['courses'].items():
            assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}")

            for chapter_slug, chapter_data in course_data['chapters'].items():
                assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}")

                for page_slug in chapter_data['pages']:
                    assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md")
