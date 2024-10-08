import random
from functools import lru_cache
from db.db import DB, Topic, OutlineEntity, Chapter, Page, Interactive, PageInteractive
from src.events.events import CompiledInteractivesToChallengePage


class CompileInteractivesToChallengePagesHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])

    def handle(self):
        challenge_pages = self._get_challenge_pages()
        challenge_interactives_count = self._get_topic_interactive_count_settings()['challenge']
        already_associated_interactive_ids = [i[0] for i in self.db.query(PageInteractive.interactive_id).all()]

        chapter_count = 0
        for page in challenge_pages:
            chapter_count += 1
            chapter_id = page.chapter_id
            interactives = self._get_chapter_interactives(chapter_id)
            remaining_interactives = [i for i in interactives if i.id not in already_associated_interactive_ids]
            if len(remaining_interactives) < challenge_interactives_count:
                print(f'Not enough interactives to associate with challenge page: {page.id}')
                continue

            # Choose a random sampling from the remaining interactives to associate with the challenge page
            practice_challenge_interactives = random.sample(remaining_interactives, k=challenge_interactives_count)

            # Save to DB
            for interactive in practice_challenge_interactives:
                page_interactive = PageInteractive(
                    interactive_id=interactive.id,
                    page_id=page.id
                )
                self.db.add(page_interactive)
                already_associated_interactive_ids.append(interactive.id)
            self.db.commit()

            practice_challenge_content = self._build_challenge_page_content(chapter_count, chapter_id, practice_challenge_interactives)
            page.content = practice_challenge_content
            page.hash = Page.hash_page(practice_challenge_content)
            page.generated = True
            self.db.commit()

        return CompiledInteractivesToChallengePage(self.data)


    def _build_challenge_page_content(self, chapter_count: int, chapter_id: int, interactives: list[Interactive]):
        chapter_record = self.db.get(Chapter, chapter_id)
        page_content = f"## Practice Skill Challenge {str(chapter_count)} \n### {chapter_record.name}\n\n"
        return page_content


    def _get_chapter_interactives(self, chapter_id: int) -> list[Interactive]:
        chapter_pages = self._get_pages_from_chapter(chapter_id)
        chapter_page_ids = [page.id for page in chapter_pages]

        # We don't want to add codepen interactives to challenge pages.
        return self.db.query(Interactive).filter(
            Interactive.type != 'codepen',
            Interactive.page_source_id.in_(chapter_page_ids)
        ).order_by(
            Interactive.difficulty
        ).all()


    def _get_pages_from_chapter(self, chapter_id: int) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.chapter_id == chapter_id,
            Page.type == 'lesson'
        ).all()


    @lru_cache(maxsize=None)  # memoize
    def _get_topic_interactive_count_settings(self):
        topic_settings = self.topic.get_properties('settings')
        interactive_options = topic_settings.get('interactives', {})
        interactives_counts = interactive_options.get('counts', {
            'lesson': 1,
            'challenge': 5,
            'final-skill-challenge': 20
        })

        return interactives_counts


    @lru_cache(maxsize=None)  # memoize
    def _get_challenge_pages(self):
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.type == 'challenge',
        ).all()
