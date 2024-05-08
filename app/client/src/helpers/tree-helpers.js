import {
    AcademicCapIcon,
    DocumentTextIcon,
    BookOpenIcon,
    LightBulbIcon,
    ListBulletIcon
} from '@heroicons/vue/24/outline';

function mapPageEntity(topic, page) {
    return {
        name: page.slug,
        key: `lesson-${page.id}`,
        label: `Page: ${page.name}`,
        data: {
            topicId: topic.id,
            id: page.id,
            entityType: 'Page',
            icon: DocumentTextIcon,
            exists: page?.generated ?? false,
            url: `/pages/${page.id}`
        },
        type: 'url'
    }
}

function mapChapterEntity(topic, chapter) {
    return {
        name: chapter.slug,
        key: `lesson-${chapter.id}`,
        label: chapter.name,

        data: {
            topicId: topic.id,
            id: chapter.id,
            entityType: 'Chapter',
            icon: BookOpenIcon,
        },
    }
}

function mapCourseEntity(topic, course) {
    return {
        name: course.slug,
        key: `course-${course.id}`,
        label: course.name,
        type: 'url',
        data: {
            topicId: topic.id,
            id: course.id,
            entityType: 'Course',
            icon: AcademicCapIcon,
            url: `/courses/${course.id}`
        },
    }
}

function mapOutlineEntity(topic, outline) {
    return {
        name: outline.name,
        key: `outline-${outline.id}`,
        data: {
            topic_id: topic.id,
            id: outline.id,
            entityType: 'Outline',
            outlineData: outline.outline_data,
            icon: ListBulletIcon,
        },
        type: 'outline'
    }
}

function mapTopicEntity(topic) {
    return {
        name: topic.slug,
        key: `topic-${topic.id}`,
        label: topic.name,
        data: {
            id: topic.id,
            entityType: 'Topic',
            icon: LightBulbIcon
        }
    }
}

export function translateToTreeLibrary(data) {
    if (!data || data?.length === 0) return []

    return data.map((topic) => {
        const topicChildren = topic?.courses?.map((course) => {
            const courseChildren = course?.chapters?.map((chapter) => {
                const chapterChildren = chapter?.pages?.map((page) => {
                    return mapPageEntity(topic, page)
                })
                return {
                    ...mapChapterEntity(topic, chapter),
                    children: chapterChildren,
                }
            })
            return {
                ...mapCourseEntity(topic, course),
                children: courseChildren
            }
        })
        return {
            ...mapTopicEntity(topic),
            children: topicChildren
        }
    })
}


export function translateOutlinesToTreeLibrary(data) {
    if (!data || data?.length === 0) return []

    return data.map((topic) => {
        const topicChildren = topic?.outlines?.map((outline) => {
            const outlineChildren = outline?.courses?.map((course) => {
                const courseChildren = course?.chapters?.map((chapter) => {
                    const chapterChildren = chapter?.pages?.map((page) => {
                        return mapPageEntity(topic, page)
                    })
                    return {
                        ...mapChapterEntity(topic, chapter),
                        children: chapterChildren,
                    }
                })
                return {
                    ...mapCourseEntity(topic, course),
                    children: courseChildren
                }
            })

            const outlineName = topic.master_outline_id == outline.id ? `${outline.name} (Master)` : outline.name

            return {
                ...mapOutlineEntity(topic, outline),
                label: outlineName,
                children: outlineChildren,
            }
        })
        return {
            ...mapTopicEntity(topic),
            children: topicChildren
        }
    })
}