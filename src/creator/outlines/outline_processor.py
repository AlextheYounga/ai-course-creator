import os
from termcolor import colored
from dotenv import load_dotenv
from db.db import db_client, Topic, Outline, Page
from src.utils.files import read_yaml_file
from src.utils.strings import slugify, string_hash
import yaml


load_dotenv()
DB = db_client()


class OutlineProcessor:
    def __init__(self, outline_id: int):
        self.outline_id = outline_id
        self.outline = DB.get(Outline, self.outline_id)
        self.topic = self.outline.topic
        self.output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'


    def _get_page_type(self, chapter_object: dict, name: str):
        if chapter_object['name'] == "Final Skill Challenge":
            return 'final-skill-challenge'
        
        page_index = chapter_object['pages'].index(name)

        if ('Challenge' in name) and (page_index == len(chapter_object['pages']) - 1):
            return 'challenge'

        return 'page'

    def _create_page_object(self, data):
        course_slug = data['courseSlug']
        chapter_slug = data['chapterSlug']
        page_slug = data.get('slug', slugify(data['name']))
        page_path = f"{self.output_directory}/{self.topic.slug}/{self.outline.name}/content/{course_slug}/{chapter_slug}/page-{page_slug}.md"
        page_link = f"/page/{self.topic.slug}/{course_slug}/{chapter_slug}/{page_slug}"
        exists = os.path.exists(page_path)

        return {
            'name': data['name'],
            'topicSlug': self.topic.slug,
            'courseSlug': course_slug,
            'chapterSlug': chapter_slug,
            'slug': page_slug,
            'path': page_path,
            'position': data['position'],
            'positionInCourse': data['positionInCourse'],
            'positionInSeries': data['positionInSeries'],
            'type': data.get('type', 'page'),
            'exists': exists,
            'permalink': page_link,
            'link': page_link if exists else '#',
        }


    def _build_nested_outline_metadata(self):
        metadata = {
            'topic': self.topic.name,
            'topicSlug': self.topic.slug,
            'totalPages': 0,
            'courses': {},
            'allPaths': []
        }

        for course_index, course in enumerate(self.outline.master_outline):
            page_position_in_course = 0
            course = course['course']
            course_slug = slugify(course['courseName'])

            # Building course
            course_object = {
                "courseName": course['courseName'],
                'slug': course_slug,
                "chapters": {},
                "level": course_index,
                "pageCount": 0,
                'paths': [],
                'links': []
            }

            for chapter_index, chapter in enumerate(course['chapters']):
                # Building chapter object
                chapter_name = chapter['name']
                chapter_slug = chapter['slug']
                chapter_page_count = len(chapter['pages'])
                course_object['pageCount'] += chapter_page_count

                chapter_object = {
                    'name': chapter_name,
                    'slug': chapter_slug,
                    'pageCount': chapter_page_count,
                    'position': chapter_index,
                    'pages': {},
                    'paths': []
                }

                # Building page object
                for page_index, page in enumerate(chapter['pages']):
                    if not isinstance(page, str): continue

                    page_object = self._create_page_object({
                        'name': page,
                        'courseSlug': course_slug,
                        'chapterSlug': chapter_slug,
                        'position': page_index,
                        'type': self._get_page_type(chapter, page),
                        'positionInCourse': page_position_in_course,
                        'positionInSeries': len(metadata['allPaths']),
                    })

                    chapter_object['pages'][page_object['slug']] = page_object
                    chapter_object['paths'].append(page_object['path'])
                    course_object['paths'].append(page_object['path'])

                    metadata['links'].append(page_object['link'])
                    metadata['allPaths'].append(page_object['path'])

                course_object['chapters'][chapter_slug] = chapter_object

            metadata['totalPages'] += course_object['pageCount']
            metadata['courses'][course_slug] = course_object

        return metadata


    def _build_page_metadata_list(self):
        metadata = []

        for course_index, course in enumerate(self.outline.master_outline):
            page_position_in_course = 0
            course = course['course']
            course_slug = slugify(course['courseName'])

            for chapter_index, chapter in enumerate(course['chapters']):
                chapter_name = chapter.get('chapter', False) or chapter['name']
                chapter_slug = slugify(chapter_name)

                for page_index, page in enumerate(chapter['pages']):
                    if not isinstance(page, str): continue

                    page_object = self._create_page_object({
                        'name': page,
                        'courseSlug': course_slug,
                        'chapterSlug': chapter_slug,
                        'type': self._get_page_type(chapter, page),
                        'position': page_index,
                        'positionInCourse': page_position_in_course,
                        'positionInSeries': len(metadata),
                    })

                    page_object['courseData'] = {
                        'course': {
                            "name": course['courseName'],
                            'slug': course_slug,
                            'level': course_index,
                            'outline': yaml.dump(course, sort_keys=False),
                        },
                        'chapter': {
                            'name': chapter_name,
                            'slug': chapter_slug,
                            'position': chapter_index,
                            'outline': yaml.dump(course, sort_keys=False),
                        }
                    }

                    page_position_in_course += 1
                    metadata.append(page_object)
        return metadata


    @staticmethod
    def hash_outline(outline_data):
        # Convert outline text to deterministic hash for comparison
        if isinstance(outline_data, dict) or isinstance(outline_data, list):
            outline_data = str(yaml.dump(outline_data, sort_keys=False)).strip()
        if isinstance(outline_data, str):
            outline_data = outline_data.strip()

        try:
            return string_hash(outline_data)
        except Exception:
            return None


    @staticmethod
    def get_or_create_outline_record_from_file(topic_id: int, outline_file: str):
        outline = OutlineProcessor.get_outline_record_from_file(outline_file)
        if outline: return outline

        print(colored("Detected outline changes.\n", "green"))
        return OutlineProcessor.create_new_outline_from_file(topic_id, outline_file)


    @staticmethod
    def get_outline_record_from_file(outline_file: str):
        outline_data = open(outline_file).read()
        outline_hash = OutlineProcessor.hash_outline(outline_data)
        outline = DB.query(Outline).filter(Outline.hash == outline_hash).first()

        if outline:
            return outline
        return None


    @staticmethod
    def create_new_outline_from_file(topic_id: int, outline_file: str):
        # Create new outline record
        topic = DB.get(Topic, topic_id)

        last_outline = DB.query(Outline).filter(
            Outline.topic_id == topic_id
        ).order_by(
            Outline.id.desc()
        ).first()

        new_outline = Outline.instantiate(topic)
        new_outline.skills = last_outline.skills
        new_outline.draft_outline = last_outline.draft_outline
        new_outline.master_outline = read_yaml_file(outline_file)  # Add changed outline to record
        new_outline.hash = OutlineProcessor.hash_outline(new_outline.master_outline)

        DB.add(new_outline)
        DB.commit()

        return new_outline


    @staticmethod
    def get_outline_metadata(outline_id: int, format: str = 'list'):
        processor = OutlineProcessor(outline_id)

        if (format == 'nested'):
            return processor._build_nested_outline_metadata()

        return processor._build_page_metadata_list()



    @staticmethod
    def dump_pages_from_outline(outline_id: int):
        outline = DB.get(Outline, outline_id)
        topic = outline.topic

        output_directory = os.environ.get("OUTPUT_DIRECTORY") or 'out'
        output_path = f"{output_directory}/{topic.slug}"

        outline_rows = OutlineProcessor.get_outline_metadata(outline_id)

        for row in outline_rows:
            page_path = row['path']

            page = DB.query(Page).filter(
                Page.topic_id == topic.id,
                Page.course_slug == row['courseSlug'],
                Page.chapter_slug == row['chapterSlug'],
                Page.slug == row['slug']
            ).first()

            if not page or not page.content: continue

            print(colored(f"Writing page: {page_path}", "green"))

            os.makedirs(os.path.dirname(page_path), exist_ok=True)
            with open(page_path, 'w') as f:
                f.write(page.content)
                f.close()

        with open(f"{output_path}/{outline.name}/skills.yaml", 'w') as skills_file:
            skills_file.write(yaml.dump(outline.skills, sort_keys=False))
            skills_file.close()

        with open(f"{output_path}/{outline.name}/draft-outline.yaml", 'w') as draft_file:
            draft_file.write(yaml.dump(outline.draft_outline, sort_keys=False))
            draft_file.close()

        with open(f"{output_path}/{outline.name}/outline.yaml", 'w') as outline_file:
            outline_file.write(yaml.dump(outline.master_outline, sort_keys=False))
            outline_file.close()
