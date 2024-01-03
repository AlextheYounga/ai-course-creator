import inquirer


def main():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=[
                          'Generate Course Outlines',
                          'Generate Course Pages'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['subroutine']

    if answer == 'Generate Course Outlines':
        from src.openai.outline_creator import run_outline_creator
        run_outline_creator()
    elif answer == 'Generate Course Pages':
        from src.openai.page_material_creator import run_page_creator
        run_page_creator()
    else:
        "You did not select a subroutine. Exiting..."


if __name__ == '__main__':
    main()
