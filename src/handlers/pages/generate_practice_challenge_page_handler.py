from db.db import DB, Topic, Page, Outline, OutlineEntity
from openai import OpenAI
from termcolor import colored
from .prompts.build_practice_challenge_prompt_handler import BuildPracticeChallengePromptHandler
import progressbar


class GeneratePracticeChallengePageHandler:
    def __init__(self, topic_id: int, llm: OpenAI, pages: list[Page]):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm
        self.pages = [page for page in pages if page.type == 'challenge']
        self.outline = Outline.get_master_outline(DB, self.topic)


    def handle(self):
        generated_pages = []
        total_count = len(self.pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True).start() as bar:
            # Loop through outline pages
            for page in self.pages:
                preprocessed_page = self.preprocess_page(page)

                chapter_incomplete = self._check_chapter_incomplete(preprocessed_page)
                if chapter_incomplete:
                    print(colored(f"Skipping incomplete chapter {page.chapter_slug}...", "yellow"))
                    bar.increment()
                    continue

                generated_page = self.generate_practice_skill_challenge(preprocessed_page)
                generated_pages.append(generated_page)

                bar.increment()

        return generated_pages



    def preprocess_page(self, page: Page):
        page = Page.check_for_existing_page_material(DB, page)


    def generate_practice_skill_challenge(self, page: Page):
        # Build messages
        prompt_handler = BuildPracticeChallengePromptHandler(self.outline, page)
        messages = prompt_handler.handle()

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('practice-skill-challenge', messages, options={})
        material = validated_response['content']

        # Update page record
        page.content = material
        page.hash = Page.hash_page(material)
        page.link = page.permalink
        page.generated = True

        # Save to Database
        DB.commit()

        # Write to file
        page.dump_page()

        return page


    def _check_chapter_incomplete(self, page: Page):
        chapter_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.course_id == page.course_id,
            Page.chapter_id == page.chapter_id,
            Page.type == 'lesson',
            Page.active == True,
        ).all()

        return True in [page.content == None for page in chapter_pages]
