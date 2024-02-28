
from db.db import DB, Topic, Page, Outline, OutlineEntity
from openai import OpenAI
from termcolor import colored
from .prompts.build_final_skill_challenge_prompt_handler import BuildFinalSkillChallengePromptHandler
import progressbar



class GenerateFinalSkillChallengePageHandler:
    def __init__(self, topic_id: int, llm: OpenAI, pages: list[Page]):
        self.topic = DB.get(Topic, topic_id)
        self.llm_handler = llm
        self.pages = [page for page in pages if page.type == 'final-skill-challenge']
        self.outline = Outline.get_master_outline(DB, self.topic)

    def handle(self):
        generated_pages = []
        total_count = len(self.pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating pages: ', redirect_stdout=True).start() as bar:
            # Loop through outline pages
            for page in self.pages:
                preprocessed_page = self.preprocess_page(page)

                course_incomplete = self._check_course_incomplete(page)
                if course_incomplete:
                    print(colored(f"Skipping incomplete course '{page.course_slug}'...", "yellow"))
                    bar.increment()
                    continue

                generated_page = self.generate_practice_skill_challenge(preprocessed_page)
                generated_pages.append(generated_page)

                bar.increment()

        return generated_pages


    def generate_final_skill_challenge(self, page: Page):
        # Build messages
        prompt_handler = BuildFinalSkillChallengePromptHandler(self.outline, page)
        messages = prompt_handler.handle()

        # Send to ChatGPT
        validated_response = self.ai_client.send_prompt('final-skill-challenge', messages, options={})
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


    def create_from_outline(self):
        generated_pages = []
        entities = Outline.get_entities(DB, self.outline.id)
        fsc_pages = [page for page in entities['pages'] if page.type == 'final-skill-challenge']
        total_count = len(fsc_pages)

        with progressbar.ProgressBar(max_value=total_count, prefix='Generating final skill challenges: ', redirect_stdout=True).start() as bar:
            for page in fsc_pages:
                page = Page.check_for_existing_page_material(DB, page)



                page = self.generate_final_skill_challenge(page)
                generated_pages.append(page)

                bar.increment()

        return generated_pages


    # Prompts






    def _check_course_incomplete(self, page: Page):
        course_pages = DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == "Page",
            Page.course_slug == page.course_slug,
            Page.type == 'page',
            Page.active == True,
        ).all()

        return True in [page.content == None for page in course_pages]
