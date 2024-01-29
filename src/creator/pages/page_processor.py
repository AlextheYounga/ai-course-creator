import os
from dotenv import load_dotenv
from termcolor import colored
from db.db import DB, Page
from src.utils.strings import string_hash


load_dotenv()


class PageProcessor:
    @staticmethod
    def dump_page(page: Page):
        print(colored(f"Writing page: {page.path}", "green"))

        os.makedirs(os.path.dirname(page.path), exist_ok=True)
        with open(page.path, 'w') as f:
            f.write(page.content)
            f.close()


    @staticmethod
    def dump_pages(pages: list[Page]):
        for page in pages:
            PageProcessor.dump_page(page)


    @staticmethod
    def hash_page(content):
        page_material = content.strip()

        try:
            return string_hash(page_material)
        except Exception:
            return None


    @staticmethod
    def handle_existing_page_material(page: Page):
        material = open(page.path, 'r').read()
        hash = PageProcessor.hash_page(material)

        if page.hash != hash:
            page.content = material
            page.generated = True
            page.link = page.permalink
            page.hash = hash

            DB.add(page)
            DB.commit()

            return True
        return False


    @staticmethod
    def check_for_existing_page_material(page: Page) -> bool:
        existing_content = page.content != None
        file_exists = os.path.exists(page.path)

        if file_exists and not existing_content:
            return PageProcessor.handle_existing_page_material(page)

        return existing_content
