from db.db import DB, Course, Chapter, Outline, OutlineEntity, Page
from src.utils.parsing import parse_markdown

db = DB()


class CourseController:
    @staticmethod
    def get_course(id: int):
        course_record = db.get(Course, id)
        return course_record.to_dict()

    @staticmethod
    def get_course_chapters(course_id: int, outline_id: int):
        chapters = db.query(Chapter).join(
            OutlineEntity, OutlineEntity.entity_id == Chapter.id
        ).filter(
            OutlineEntity.outline_id == outline_id,
            OutlineEntity.entity_type == 'Chapter',
            Chapter.course_id == course_id,
        ).order_by(
            Chapter.position
        ).all()

        return [c.to_dict() for c in chapters]

    @staticmethod
    def get_course_pages(course_id: int, outline_id: int):
        pages = []
        course_pages = db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline_id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == course_id,
        ).order_by(
            Page.position_in_course
        ).all()

        for page_record in course_pages:
            interactive_records = page_record.interactives
            pages.append({
                **page_record.to_dict(),
                'interactives': [i.apply_formats().to_dict() for i in interactive_records],
                'content': str(parse_markdown(page_record.content))
            })

        return pages

    @staticmethod
    def get_course_content(id: int):
        course_record = db.get(Course, id)
        topic = course_record.topic
        outline = db.get(Outline, topic.master_outline_id)
        course = course_record.to_dict()
        chapters = CourseController.get_course_chapters(id, outline.id)
        pages = CourseController.get_course_pages(id, outline.id)
        course.update({"chapters": chapters, 'pages': pages})
        return course
