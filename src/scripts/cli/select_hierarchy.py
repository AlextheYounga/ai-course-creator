import inquirer


def select_hierarchy():
    levels = [
        'Topic',
        'Course',
        'Chapter',
        'Page',
    ]

    select_level = [
        inquirer.List('level',
                      message="Select hierarchy level.",
                      choices=levels),
    ]

    choice = inquirer.prompt(select_level)
    level = choice['level']
    return level
