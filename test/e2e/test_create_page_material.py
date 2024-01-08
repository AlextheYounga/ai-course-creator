import shutil
import os
from src.utils.chat_helpers import slugify
from src.openai.page_material_creator import PageMaterialCreator
from ..mocks.openai_mock_service import OpenAIMockService

# What the outline looks like before we run page material creator
PATHLESS_MASTER_OUTLINE = 'test/fixtures/data/pathless-master-outline.json'
OUTPUT_PATH = "test/out"


# Setup paths
slug = 'ruby-on-rails'
if (os.path.exists(f"{OUTPUT_PATH}/{slug}")):
    shutil.rmtree(f"{OUTPUT_PATH}/{slug}")

os.makedirs(f"{OUTPUT_PATH}/{slug}", exist_ok=True)
shutil.copy(PATHLESS_MASTER_OUTLINE, f"{OUTPUT_PATH}/{slug}/master-outline.json")

# Semi decent happy path test
def test_create_page_material():
    topics = ['Ruby on Rails']
    for topic in topics:

        # Initialize OpenAI
        session_name = f"{topic} Page Material"
        ai_client = OpenAIMockService(session_name)

        creator = PageMaterialCreator(topic, ai_client, OUTPUT_PATH)
        outline = creator.create_pages_from_outline()

        assert len(os.listdir(f"{OUTPUT_PATH}/{slug}/content")) == 15

        for course in outline['courses']:
            course_slug = course['slug']
            assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}")

            for chapter in course['chapters']:
                chapter_slug = chapter['slug']
                assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}")

                for page_slug in chapter['pageSlugs']:
                    assert os.path.exists(f"{OUTPUT_PATH}/{slug}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md")
