from db.db import DB, Topic, Page, Outline
from openai import OpenAI
from .summarize_page_handler import SummarizePageHandler
from .prompts.build_lesson_page_prompt_handler import BuildLessonPagePromptHandler
import progressbar



class GenerateLessonPageHandler:
    def __init__(self, topic_id: int, llm: OpenAI, pages: list[Page]):
        self.topic = DB.get(Topic, topic_id)
        self.llm_hander = llm
        self.pages = [page for page in pages if page.type == 'lesson']
        self.outline = Outline.get_master_outline(DB, self.topic)


    def handle(self):
        generated_pages = []
        total_count = len(self.pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True).start() as bar:
            # Loop through outline pages
            for page in self.pages:
                preprocessed_page = self.preprocess_page(page)
                generated_page = self.generate_page_material(preprocessed_page)
                postprocessed_page = self.postprocess_page(generated_page)
                generated_pages.append(postprocessed_page)

                bar.increment()

        return generated_pages


    def preprocess_page(self, page: Page):
        return Page.check_for_existing_page_material(DB, page)


    def generate_page_material(self, page: Page):
        # Build prompt
        prompt_handler = BuildLessonPagePromptHandler(self.outline, page)
        messages = prompt_handler.handle()

        # Send to ChatGPT
        validated_response = self.llm_hander.send_prompt('page-material', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = Page.hash_page(material)
        page.link = page.permalink
        page.generated = True

        # Save to Database
        DB.commit()

        return page


    def postprocess_page(self, page: Page) -> Page:
        # Summarize Page
        handler = SummarizePageHandler(page, self.llm_hander)
        page = handler.handle()

        # Write to file
        page.dump_page()

        return page
