from db.db import DB, Topic, Outline

db = DB()


class TopicController:
    @staticmethod
    def new(topic_name: str):
        topic_record = db.query(Topic).filter(Topic.name == topic_name).first()
        if topic_record: return topic_record

        new_topic_record = Topic(
            name=topic_name,
            slug=Topic.make_slug(topic_name),
        )

        # Save topic to database
        db.add(new_topic_record)
        db.commit()

        return new_topic_record.to_dict()


    @staticmethod
    def destroy(topic_id: int):
        topic_record = db.query(Topic).get(topic_id)
        if not topic_record: return {"error": "Topic not found"}, 404

        for outline in topic_record.outlines:
            db.delete(outline)
        for course in topic_record.courses:
            db.delete(course)
        for chapter in topic_record.chapters:
            db.delete(chapter)
        for page in topic_record.pages:
            db.delete(page)


        db.delete(topic_record)
        db.commit()

        return {"message": "Topic deleted"}


    @staticmethod
    def get_all():
        topics = []
        topic_records = db.query(Topic).all()

        if topic_records:
            # Join outlines in response
            for topic in topic_records:
                topics.append({
                    **topic.to_dict(),
                    "outlines": [outline.to_dict() for outline in topic.outlines],
                })

        return topics


    @staticmethod
    def get_all_topics_materials():
        """
        Returns: topics->courses->chapters->pages
        """
        course_material = []

        topics = db.query(Topic).all()
        if not topics: return []

        for topic in topics:
            outline = Outline.get_master_outline(db, topic)

            topic_data = {**topic.to_dict(), 'courses': []}

            if outline:
                outline_entities = Outline.get_entities(db, outline.id)

                # Loop through courses
                for course in outline_entities['courses']:
                    course_object = {**course.to_dict(), 'chapters': []}

                    chapter_records = [
                        chapter for chapter in outline_entities['chapters']
                        if chapter.course_id == course.id
                    ]

                    # Loop through chapters
                    for chapter in chapter_records:
                        page_records = [
                            page for page in outline_entities['pages']
                            if (page.course_id == course.id and page.chapter_id == chapter.id)
                        ]

                        # Add chapter pages to chapter
                        chapter_object = {
                            **chapter.to_dict(),
                            'pages': [page.to_dict() for page in page_records]
                        }

                        course_object['chapters'].append(chapter_object)
                    topic_data['courses'].append(course_object)
            course_material.append(topic_data)
        return course_material
