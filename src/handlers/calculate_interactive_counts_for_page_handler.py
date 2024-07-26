from functools import lru_cache
import random
from db.db import DB, Topic, Course, Outline, OutlineEntity, Page
from src.events.events import InteractiveCountsCalculatedForPage


class CalculateInteractiveCountsForPageHandler:
    """
    Warning: this handler does math!

    We have to determine how many interactives to generate for a page based on number of pages and the user's settings.
    We get the total number of lesson pages and chapters, then add up how many interactives we'll need for each challenge type. Then we'll divide by the total 
    number of pages to get the interactives per page value. 

    Then we have to determine which and how many of each interactive type to generate per page. I use a weighted random.choices() function to arrive at
    this number, which is cleaner than brute-forcing a set number of types of generate per page, because you can easily end up with a remainder 
    of interactives that we'll have to pile up on the final skill challenge. (When I first tried forcing a fixed number per type, I ended up 
    with an 80-question final skill challenge!) Using a random.choices() function allows us to distribute the interactive types more evenly across pages.

    The user can add preferred weights in the topic settings to the interactives to influence how often a particular type of interactive is generated. 
    """

    def __init__(self, data: dict):
        self.data = data
        self.db = DB()
        self.outline = self.db.get(Outline, data['outlineId'])
        self.page = self.db.get(Page, data['pageId'])
        self.topic = self.db.get(Topic, data['topicId'])


    def handle(self):
        # Get total lesson and chapter counts from outline
        total_page_count = len(self._get_total_course_lesson_pages())
        course_chapter_count = self._get_course_chapter_count()

        # Get user topic settings for interactive counts
        interactive_count_settings = self._get_topic_interactive_count_settings()

        # Calculate total number of questions to generate and interactives per page
        lesson_interactives = total_page_count * interactive_count_settings['lesson']  # default 1
        chapter_interactives = course_chapter_count * interactive_count_settings['challenge']  # default 5
        final_interactives = interactive_count_settings['final-skill-challenge']  # default 20
        buffer = 5

        total_questions = lesson_interactives + chapter_interactives + final_interactives + buffer
        interactives_per_page = round(total_questions / total_page_count)

        # Use weights from user settings to randomly select interactive types for each page
        # The weights will increase/decrease the likelihood of a certain interactive type being selected
        # This allows us to distribute interactives more evenly across pages
        interactives_weights = self._get_interactive_weights_from_settings()
        interactive_types = list(interactives_weights.keys())
        choice_weights = [int(w * 10) for w in list(interactives_weights.values())]

        page_interactive_choices = random.choices(interactive_types, weights=choice_weights, k=interactives_per_page)

        page_interactives_to_generate = {}
        for interactive_type in interactive_types:
            page_interactives_to_generate[interactive_type] = page_interactive_choices.count(interactive_type)

        self._save_interactive_info_to_course_properties({
            'totalCount': total_questions,
            'perPage': interactives_per_page,
            'totallesson_interactives': lesson_interactives,
            'totalChallengeInteractives': chapter_interactives,
            'totalFinalInteractives': final_interactives,
            'weights': interactives_weights,
        })

        self._save_interactives_to_page_properties(page_interactives_to_generate)

        return InteractiveCountsCalculatedForPage({
            **self.data,
            'courseId': self._get_page_course().id,
            'interactives': page_interactives_to_generate
        })


    def _get_topic_interactive_count_settings(self):
        default_lesson_interactive_count = 1
        default_practice_challenge_interactive_count = 5
        default_final_skill_challenge_interactive_count = 20

        topic_settings = self._get_topic_settings()
        interactive_options = topic_settings.get('interactives', {})
        interactives_counts = interactive_options.get('counts', {
            'lesson': default_lesson_interactive_count,
            'challenge': default_practice_challenge_interactive_count,
            'final-skill-challenge': default_final_skill_challenge_interactive_count
        })

        return interactives_counts


    def _get_interactive_weights_from_settings(self):
        default_page_interactives_weight = {
            'multipleChoice': 0.6,
            'codeEditor': 0.4,
        }

        topic_settings = self._get_topic_settings()
        interactive_options = topic_settings.get('interactives', {})
        interactives_weights = interactive_options.get('weights', default_page_interactives_weight)

        # If topic does not allow codepen or code_editor, add their weights to multipleChoice
        if not self._topic_allows_code_editor() and 'codeEditor' in interactives_weights:
            del interactives_weights['codeEditor']
        if not self._topic_allows_codepen() and 'codepen' in interactives_weights:
            del interactives_weights['codepen']

        # Account for remainders in weights
        total_weight = sum(interactives_weights.values())
        remainder = 1 - total_weight
        for interactive_type in interactives_weights:
            interactives_weights[interactive_type] += remainder / len(interactives_weights)

        return interactives_weights


    def _get_course_chapter_count(self):
        pages = self._get_total_course_lesson_pages()
        chapter_ids = [page.chapter_id for page in pages]
        return len(set(chapter_ids))


    def _topic_allows_code_editor(self):
        # Check topic settings for codepen settings.
        # If it's not set, default to allowing codepen
        # If prompts are not of collection 'programming', do not allow codepen.
        topic_settings = self._get_topic_settings()
        interactive_options = topic_settings.get('interactives', {})
        allows_codepen = interactive_options.get('code_editor', True)

        prompt_collection = self.topic.get_properties('prompts')
        if prompt_collection != 'programming':
            allows_codepen = False

        return allows_codepen


    def _topic_allows_codepen(self):
        # Default is false because there are inherently fewer languages supported by codepen
        topic_settings = self._get_topic_settings()
        interactive_options = topic_settings.get('interactives', {})
        allows_codepen = interactive_options.get('codepen', False)

        return allows_codepen

    def _save_interactive_info_to_course_properties(self, info: dict):
        course = self._get_page_course()
        course.update_properties(self.db, {
            "hasInteractives": True,
            'interactives': info,
        })


    def _save_interactives_to_page_properties(self, interactives):
        interactives_count = sum(interactives.values())
        self.page.update_properties(self.db, {
            'interactivesCount': interactives_count,
        })


    @lru_cache(maxsize=None)  # memoize
    def _get_total_course_lesson_pages(self):
        return self.db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == self.outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.type == 'lesson',
            Page.course_id == self.page.course_id
        ).all()


    @lru_cache(maxsize=None)  # memoize
    def _get_topic_settings(self):
        return self.topic.get_properties('settings')


    @lru_cache(maxsize=None)  # memoize
    def _get_page_course(self):
        return self.db.query(Course).filter(
            Course.id == self.page.course_id
        ).first()
