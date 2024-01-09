function translateToTableRows(data) {
    const rows = []

    for (topic of data) {
        if (!Object.keys(topic?.courses)?.length) continue
        const topicSlug = topic.topic.toLowerCase().replaceAll(' ', '-')

        for (const [courseSlug, courseData] of Object.entries(topic.courses)) {
            if (!Object.keys(courseData?.chapters)?.length) continue

            for (const [chapterSlug, chapterData] of Object.entries(courseData.chapters)) {
                if (!Object.keys(chapterData?.pages)?.length) continue

                for (const [pageSlug, pageData] of Object.entries(chapterData.pages)) {

                    function _generateRowLink() {
                        if (pageData?.exists && pageData?.path) {
                            return `/page/${topicSlug}/${courseSlug}/${chapterSlug}/${pageSlug}`
                        }
                        return '#'
                    }

                    rows.push({
                        id: `${topicSlug}/${courseSlug}/${chapterSlug}/${pageSlug}`,
                        group: `${topic.topic} | Course: ${courseData.courseName}`,
                        topic: topic?.topic ?? 'Not found',
                        course: courseData?.courseName ?? 'Not found',
                        chapter: chapterData?.name ?? 'Not found',
                        page: pageData?.name ?? 'Not found',
                        link: _generateRowLink(),
                        exists: pageData?.exists ?? false,
                    })
                }
            }
        }
    }

    return rows
}

function logColor(line) {
    let color = '';
    if (line.includes('RESPONSE')) {
        return 'text-green-500'
    }
    if (line.includes('SEND')) {
        return 'text-yellow-500'
    }
    return color
}

function displayLogText(line) {
    if (line.includes('RESPONSE')) {
        return 'RESPONSE: ' + line
    }
    if (line.includes('SEND')) {
        return 'SEND: ' + line
    }

    return line.substring(0, 100)
}