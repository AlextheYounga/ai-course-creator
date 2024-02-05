import inquirer


def select_content_function(hierarchy: str):

    content_functions = {
        'Topic': [
            'All',
            'Page Material',
            'Practice Skill Challenges',
            'Final Skill Challenges',
        ],
        'Course': [
            'All',
            'Page Material',
            'Practice Skill Challenges',
            'Final Skill Challenges',
        ],
        'Chapter': [
            'All',
            'Page Material',
            'Practice Skill Challenges',
        ],
    }

    content_types = content_functions[hierarchy]

    select_content_type = [
        inquirer.List('contentType',
                      message="Select hierarchy to generate material.",
                      choices=content_types),
    ]

    choice = inquirer.prompt(select_content_type)
    content_type = choice['contentType']

    return content_type