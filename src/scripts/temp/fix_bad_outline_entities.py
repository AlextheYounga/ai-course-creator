from db.db import DB, Topic, OutlineEntity, Outline, Page

topics = DB.query(Topic).all()
for topic in topics:
    print(topic.name)
    outline = DB.query(Outline).filter(
        Outline.id == topic.master_outline_id
    ).first()

    if outline:
        soft_deleted_pages = DB.query(Page).filter(
            Page.topic_id == topic.id,
            Page.active == False
        ).all()

        for page in soft_deleted_pages:
            new_page = DB.query(Page).filter(
                Page.topic_id == topic.id,
                Page.course_id == page.course_id,
                Page.chapter_id == page.chapter_id,
                Page.name == page.name,
                Page.active == True
            ).first()

            entity = DB.query(OutlineEntity).filter(
                OutlineEntity.entity_type == 'Page',
                OutlineEntity.entity_id == new_page.id,
                OutlineEntity.outline_id == outline.id
            ).first()

            if (not entity):
                print(f"Creating outline entity for page {new_page.name}")
                OutlineEntity.first_or_create(DB, outline.id, new_page)
