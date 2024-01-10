// jQuery, what a blast from the past...
function ajaxFetch(url, callback) {
    try {
        $.ajax({
            url: url,  // the endpoint on your Flask app
            type: 'POST',  // http method
            contentType: 'application/json',  // type of data being sent
            success: function (response) {  // A function to be called if the request succeeds
                console.log("Success: ", url);
                callback(response)
            },
            error: function (xhr) {
                // Handle error
                console.error("Error occurred: ", xhr);
            }
        });
    } catch (error) {
        console.error("Error occurred: ", xhr);
        alert("Error occurred: " + error);
    }
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

function translateToRows(data) {
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

function translateToTreeStructure(data) {
    const tree = []
    let topicId = 0

    for (topic of data) {
        if (!Object.keys(topic?.courses)?.length) continue
        const topicSlug = topic.topic.toLowerCase().replaceAll(' ', '-')

        const topicNode = {
            name: topic.topic,
            id: `topic-${topicId++}`,
            children: []
        }

        let courseId = 0
        for (const [courseSlug, courseData] of Object.entries(topic.courses)) {
            if (!Object.keys(courseData?.chapters)?.length) continue
            const courseNode = {
                name: `Course: ${courseData.courseName}`,
                id: `course-${courseId++}`,
                children: []
            }

            let chapterId = 0
            for (const [chapterSlug, chapterData] of Object.entries(courseData.chapters)) {
                if (!Object.keys(chapterData?.pages)?.length) continue

                const chapterNode = {
                    name: `Chapter: ${chapterData.name}`,
                    id: `chapter-${chapterId++}`,
                    children: []
                }

                let pageId = 0
                for (const [pageSlug, pageData] of Object.entries(chapterData.pages)) {
                    function _generateRowLink() {
                        if (pageData?.exists && pageData?.path) {
                            return `/page/${topicSlug}/${courseSlug}/${chapterSlug}/${pageSlug}`
                        }
                        return '#'
                    }

                    chapterNode.children.push({
                        name: `Page: ${pageData.name}`,
                        id: `page-${pageId++}`,
                        exists: pageData?.exists ?? false,
                        url: _generateRowLink()
                    })
                }
                courseNode.children.push(chapterNode)
            }
            topicNode.children.push(courseNode)
        }
        tree.push(topicNode)
    }

    return tree
}

function createExistsIcon(exists) {
    return `<span class="pt-1.5 pl-2">
        <div class="exists-icon flex-none rounded-full p-1${ exists ? ' text-green-400 bg-green-400/10' : 'text-rose-400 bg-rose-400/10'}">
            <div class="h-1.5 w-1.5 rounded-full bg-current"></div>
        </div>
    </span>`
}


function displayData(data) {
    const tree = translateToTreeStructure(data)
    $('#tree').tree({
        data: tree,
        autoOpen: true,
        dragAndDrop: false,
        onCreateLi: function(node, $li) {
            if (node.url && node.exists) {
                $li.find('.jqtree-element').append(createExistsIcon(node.exists));
            }

        }
    });

    $('#tree').bind(
        'tree.click',
        function (event) {
            // The clicked node is 'event.node'
            var node = event.node;
            var theURL = node.url;
            if (theURL) {
                location.href = theURL;
            }
        }
    );
}

function displayActivity(data) {
    const logList = $('#log-list')
    const logLine = $('#log-line')

    logList.find('.clone').remove()

    for (line of data) {
        // const logId = line.substring(0, 23) // date timestamp

        const lineColor = logColor(line)
        const displayText = displayLogText(line)
        const newLine = logLine.clone()

        newLine.removeClass('hidden')
        newLine.addClass('clone')
        newLine.addClass(lineColor)
        newLine.text(displayText)
        logList.append(newLine)
    }
}