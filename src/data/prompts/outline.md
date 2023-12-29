Please generate an outline for a course "{course_name}" consisting of chapters and pages. For each chapter, create a list of individual pages. Try to limit the number of pages to 3, but there may be cases where another page is necessary to appropriately convey an idea. 

Please return your results in the following JSON format:
```json
[
    {
        "chapterName": "An Interesting Chapter Name",
        "pages": [
            "A Header for the First Page in Chapter",
            "A Header for the Second Page in Chapter",
            "A Header for a Third Page in Chapter",
            "A Header for a Fourth Page But Only if Necessary"
        ]
    }
]
```