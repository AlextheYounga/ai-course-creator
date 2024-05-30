from db.db import DB, Course, Outline, OutlineEntity, Page

db = DB()

# TODO: Update this


class CourseController:
    @staticmethod
    def get_course_pages(id: int):
        course = db.get(Course, id)
        topic = course.topic
        outline = db.get(Outline, topic.master_outline_id)

        return db.query(Page).join(
            OutlineEntity, OutlineEntity.entity_id == Page.id
        ).filter(
            OutlineEntity.outline_id == outline.id,
            OutlineEntity.entity_type == 'Page',
            Page.course_id == id,
        ).order_by(
            Page.position_in_course
        ).all()


    @staticmethod
    def get_course_content(id: int):
        course_content = []
        course_pages = CourseController.get_course_pages(id)

        for page in course_pages:
            if not page.content: continue

            nodes = page.get_properties()['nodes']

            material = {
                'id': page.id,
                'type': page.type,
                'nodes': nodes
            }

            course_content.append(material)


        return course_content
