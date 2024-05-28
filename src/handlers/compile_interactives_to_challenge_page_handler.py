import random
from functools import lru_cache
from db.db import DB, Topic, OutlineEntity, Chapter, Page, Interactive
from src.events.events import CompiledInteractivesToChallengePage


class CompileInteractivesToChallengePageHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.chapter_entity = self.db.get(OutlineEntity, data['outlineEntityId'])
        self.topic = self.db.get(Topic, data['topicId'])

    def handle(self):
        challenge_interactives_count = self._get_topic_interactive_count_settings()
        chapter_pages = self._get_chapter_pages()
        interactives = self._get_chapter_interactives()

        # Get interactives we've already associated chapter with pages
        already_associated_interactives = []
        for page in chapter_pages:
            already_associated_interactives += (page.interactive_ids or [])
        remaining_interactives = [i for i in interactives if i.id not in already_associated_interactives]

        # Choose a random sampling from the remaining interactives to associate with the challenge page
        practice_challenge_interactives = random.sample(remaining_interactives, k=challenge_interactives_count)

        # Associate the interactives with the challenge page
        practice_challenge_page = self._get_chapter_practice_challenge_page()
        practice_challenge_content = self._build_challenge_page_content()

        # Save to DB
        practice_challenge_page.interactive_ids = [i.id for i in practice_challenge_interactives]
        practice_challenge_page.content = practice_challenge_content
        practice_challenge_page.hash = Page.hash_page(practice_challenge_content)
        practice_challenge_page.generated = True

        self.db.commit()

        return CompiledInteractivesToChallengePage(self.data)


    def _build_challenge_page_content(self):
        chapter_record = self.db.get(Chapter, self.chapter_entity.entity_id)
        page_title = f"# Practice Skill Challenge\n## {chapter_record.name}\n\n"

        return page_title


    @ lru_cache(maxsize=None)  # memoize
    def _get_chapter_interactives(self):
        chapter_entities = self._get_chapter_outline_entity_pages()
        chapter_outline_entity_page_ids = [page.id for page in chapter_entities]

        # We don't want to add codepen interactives to challenge pages.
        return self.db.query(Interactive).filter(
            Interactive.type != 'codepen',
            Interactive.outline_entity_id.in_(chapter_outline_entity_page_ids)
        ).order_by(
            Interactive.difficulty
        ).all()


    def _get_chapter_pages(self) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.chapter_id == self.chapter_entity.entity_id,
            Page.type == 'lesson'
        ).all()


    def _get_chapter_outline_entity_pages(self) -> list[OutlineEntity]:
        return self.db.query(OutlineEntity).join(
            Page, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.chapter_id == self.chapter_entity.entity_id,
            Page.type == 'lesson'
        ).all()


    def _get_chapter_practice_challenge_page(self):
        return self.db.query(Page).filter(
            Page.chapter_id == self.chapter_entity.entity_id,
            Page.type == 'challenge'
        ).first()


    def _get_topic_interactive_count_settings(self):
        topic_settings = self.topic.get_properties('settings')
        interactive_options = topic_settings.get('interactives', {})
        interactives_counts = interactive_options.get('counts', {
            'lesson': 1,
            'challenge': 5,
            'final-skill-challenge': 20
        })

        return interactives_counts['challenge']
