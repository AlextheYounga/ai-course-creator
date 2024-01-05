function translateToTableRows(data) {
    const rows = []
    for (topic of data) {
        if (!topic?.courses?.length) continue

        for (course of topic.courses) {
            if (!course?.chapters?.length) continue

            for (chapter of course.chapters) {
                if (!chapter?.pages?.length) continue

                for (page of chapter.pages) {
                    rows.push({
                        id:`${course.slug}-${chapter.slug}-${page.slug}`,
                        group: `Course: ${course.courseName}`,
                        topic: topic.topic,
                        course: course.courseName,
                        chapter: chapter.chapterName,
                        page: page.pageName,
                        link: page.path,
                        generated: page.exists
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