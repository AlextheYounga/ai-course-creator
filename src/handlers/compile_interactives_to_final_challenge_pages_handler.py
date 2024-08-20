from functools import lru_cache
from db.db import DB, Topic, OutlineEntity, Course, Page, Interactive, PageInteractive
from src.events.events import CompiledInteractivesToFinalChallengePage


class CompileInteractivesToFinalChallengePagesHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.topic = self.db.get(Topic, data['topicId'])

    def handle(self):
        final_challenge_pages = self._get_final_challenge_pages()
        already_associated_interactive_ids = [i[0] for i in self.db.query(PageInteractive.interactive_id).all()]

        for page in final_challenge_pages:
            course_id = page.course_id
            interactives = self._get_course_interactives(course_id)
            # Remaining interactives, (may be slightly more than specified in settings due to buffer)
            final_challenge_interactives = [i for i in interactives if i.id not in already_associated_interactive_ids]

            # Save to DB
            for interactive in final_challenge_interactives:
                page_interactive = PageInteractive(
                    interactive_id=interactive.id,
                    page_id=page.id
                )
                self.db.add(page_interactive)
                already_associated_interactive_ids.append(interactive.id)
            self.db.commit()

            # Save to DB
            final_challenge_content = self._build_challenge_page_content(course_id, final_challenge_interactives)
            page.content = final_challenge_content
            page.hash = Page.hash_page(final_challenge_content)
            page.generated = True

            self.db.commit()

        return CompiledInteractivesToFinalChallengePage(self.data)


    def _build_challenge_page_content(self, course_id: int, interactives: list[Interactive]):
        course_record = self.db.get(Course, course_id)
        page_title = f"# Final Skill Challenge\n## {course_record.name}\n\n"

        interactive_shortcodes = []
        for interactive in interactives:
            interactive_shortcodes.append(interactive.get_data('shortcode'))
        page_content = '\n\n'.join(interactive_shortcodes)

        return '\n\n'.join([page_title, page_content])


    def _get_course_interactives(self, course_id: int):
        course_pages = self._get_course_pages(course_id)
        course_page_ids = [page.id for page in course_pages]

        # We don't want to add codepen interactives to challenge pages.
        return self.db.query(Interactive).filter(
            Interactive.type != 'codepen',
            Interactive.page_source_id.in_(course_page_ids)
        ).order_by(
            Interactive.difficulty
        ).all()


    def _get_course_pages(self, course_id) -> list[Page]:
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.course_id == course_id,
            Page.type == 'lesson'
        ).all()


    @lru_cache(maxsize=None)  # memoize
    def _get_final_challenge_pages(self):
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.data['outlineId'],
            OutlineEntity.entity_type == 'Page',
            Page.type == 'final-skill-challenge',
        ).all()
