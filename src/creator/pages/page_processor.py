import os
from dotenv import load_dotenv
from db.db import DB, Page
from src.utils.strings import string_hash

class PageProcessor:
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
            page.hash = hash

            DB.add(page)
            DB.commit()

            return True
        return False


    @staticmethod
    def check_for_existing_page_material(page: Page) -> bool:
        file_exists = os.path.exists(page.path)
        if file_exists:
            return PageProcessor.handle_existing_page_material(page)
        
        return page.content != None