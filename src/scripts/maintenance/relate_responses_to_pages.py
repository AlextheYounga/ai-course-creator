from db.db import DB, EventStore, Page

db = DB()

pages = db.query(Page).filter(Page.type == 'lesson').all()

for page in pages:
    page_properties = page.get_properties()
    page_properties['responseIds'] = []
    page.update_properties(db, page_properties)
    print(f'Updated page {page.id}')

events = db.query(EventStore).filter(EventStore.name == 'LessonPageResponseReceivedFromOpenAI').all()

for event in events:
    page_id = event.data.get('pageId', False)
    if not page_id: continue

    response_id = event.data.get('responseId', False)
    if not response_id: continue

    page = db.get(Page, page_id)
    page_properties = page.get_properties()

    if response_id not in page_properties['responseIds']:
        page_properties['responseIds'].append(response_id)
        page.update_properties(db, page_properties)
        print(f'Updated page {page_id} with response {response_id}')
