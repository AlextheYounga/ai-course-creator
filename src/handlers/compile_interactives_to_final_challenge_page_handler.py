import random
from functools import lru_cache
from db.db import DB, Topic, OutlineEntity, Course, Page, Interactive
from src.events.events import CompiledInteractivesToFinalChallengePage


class CompileInteractivesToFinalChallengePageHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.course_entity = self.db.get(OutlineEntity, data['outlineEntityId'])
        self.topic = self.db.get(Topic, data['topicId'])

    def handle(self):
        course_pages = self._get_course_pages()
        interactives = self._get_course_interactives()

        # Get interactives we've already associated with course pages
        already_associated_interactives = []
        for page in course_pages:
            already_associated_interactives += (page.interactive_ids or [])

        # Remaining interactives, (may be slightly more than specified in settings due to buffer)
        final_challenge_interactives = [i for i in interactives if i.id not in already_associated_interactives]

        # Associate the interactives with the challenge page
        final_challenge_page = self._get_course_final_challenge_page()
        final_challenge_content = self._build_challenge_page_content()

        # Save to DB
        final_challenge_page.interactive_ids = [i.id for i in final_challenge_interactives]
        final_challenge_page.content = final_challenge_content
        final_challenge_page.hash = Page.hash_page(final_challenge_content)
        final_challenge_page.generated = True

        self.db.commit()

        final_challenge_page.update_properties(self.db, {
            'interactives': self._compile_page_interactive_shortcodes(final_challenge_page.interactive_ids)
        })

        return CompiledInteractivesToFinalChallengePage(self.data)


    def _build_challenge_page_content(self):
        course_record = self.db.get(Course, self.course_entity.entity_id)
        page_title = f"# Final Skill Challenge\n## {course_record.name}\n\n"

        return page_title


    def _compile_page_interactive_shortcodes(self, selected_interactive_ids: list[int]):
        content = []
        interactives = self._get_course_interactives()
        selected_interactives = [i for i in interactives if i.id in selected_interactive_ids]

        for interactive in selected_interactives:
            content.append(interactive.get_data('shortcode'))

        return "\n\n".join(content)


    @ lru_cache(maxsize=None)  # memoize
    def _get_course_interactives(self):
        course_entities = self._get_course_outline_entity_pages()
        course_outline_entity_page_ids = [page.id for page in course_entities]

        # We don't want to add codepen interactives to challenge pages.
        return self.db.query(Interactive).filter(
            Interactive.type != 'codepen',
            Interactive.outline_entity_id.in_(course_outline_entity_page_ids)
        ).order_by(
            Interactive.difficulty
        ).all()


    @lru_cache(maxsize=None)  # memoize
    def _get_course_pages(self) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.course_id == self.course_entity.entity_id,
            Page.type == 'lesson'
        ).all()


    def _get_course_outline_entity_pages(self) -> list[OutlineEntity]:
        return self.db.query(OutlineEntity).join(
            Page, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.course_id == self.course_entity.entity_id,
            Page.type == 'lesson'
        ).all()


    def _get_course_final_challenge_page(self):
        return self.db.query(Page).filter(
            Page.course_id == self.course_entity.entity_id,
            Page.type == 'final-skill-challenge'
        ).first()
