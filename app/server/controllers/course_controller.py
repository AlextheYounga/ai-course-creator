from db.db import DB, Course, Chapter, Outline, OutlineEntity, Page
from src.utils.parsing import parse_markdown

db = DB()


class CourseController:
    @staticmethod
    def get_course_content(id: int):
        course_record = db.get(Course, id)
        topic = course_record.topic
        outline = db.get(Outline, topic.master_outline_id)

        course = course_record.to_dict()

        chapters = db.query(Chapter).join(
            OutlineEntity, OutlineEntity.entity_id == Chapter.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Chapter',
            Chapter.course_id == id,
        ).order_by(
            Chapter.position
        ).all()

        course.update({
            'chapters': [c.to_dict() for c in chapters]
        })

        course_pages = db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == id,
        ).order_by(
            Page.position_in_course
        ).all()

        course.update({
            'pages': []
        })

        for page_record in course_pages:
            interactives = [i.to_dict() for i in page_record.interactives]
            html_content = parse_markdown(page_record.content)
            page = page_record.to_dict()
            course['pages'].append({
                **page,
                'interactives': interactives,
                'content': str(html_content)
            })

        return course
