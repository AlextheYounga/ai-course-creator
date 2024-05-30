import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.course_draft import *
from termcolor import colored
import yaml



class RebuildOutlineFromDrafts:
    def run(self):
        db = self._db()
        drafts = db.query(CourseDraft).all()

        outline = []
        for draft in drafts:
            course = {
                'courseName': draft.title,
                'chapters': []
            }
            data = draft.data

            draft_chapters = data['chapters']
            exercises = data['exercises']
            for draft_chapter in draft_chapters:
                chapter = {
                    "name": draft_chapter['name'],
                    "pages": []
                }

                pages = [e for e in exercises if e['chapterId'] == draft_chapter['id']]

                if 'Practice Skill Challenge' in chapter['name']:
                    course['chapters'][-1]['pages'].append('Practice Skill Challenge')
                    continue

                for page in pages:
                    chapter['pages'].append(page['name'])

                course['chapters'].append(chapter)

            outline_course = {'course': course}
            outline.append(outline_course)

        with open('storage/rebuilt-outline.yml', 'w') as f:
            yaml.dump(outline, f, sort_keys=False)

    def _db(self):
        engine = create_engine('sqlite:///storage/drafts.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        return Session()


RebuildOutlineFromDrafts().run()
