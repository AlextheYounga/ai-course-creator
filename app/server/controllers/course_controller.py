from db.db import DB, Course, Outline, OutlineEntity, Page
import markdown
from flask import jsonify


class CourseController:
    @staticmethod
    def get_course_pages(id: int):
        course = DB.get(Course, id)
        topic = course.topic
        outline = DB.get(Outline, topic.master_outline_id)

        return DB.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == id,
            Page.active == True,
        ).order_by(
            Page.position_in_course
        ).all()


    @staticmethod
    def get_course_content(id: int):
        course_content = []
        course_pages = CourseController.get_course_pages(id)

        for page in course_pages:
            if not page.content: continue

            html_content = markdown.markdown(page.content, extensions=['toc', 'fenced_code'])
            material = {
                **page.to_dict(),
                'html': html_content
            }

            course_content.append(material)


        return jsonify(course_content)