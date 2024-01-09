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
                    rows.push({
                        id: `${topicSlug}/${courseSlug}/${chapterSlug}/${pageSlug}`,
                        group: `Course: ${courseData.courseName}`,
                        topic: topic.topic,
                        course: courseData.courseName,
                        chapter: chapterData.name,
                        page: pageData.name,
                        link: pageData.path,
                        exists: pageData.exists,
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