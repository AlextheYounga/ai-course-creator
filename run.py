import inquirer


def main():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine",
                      choices=[
                          'Generate Courses',
                          'Generate Outline',
                          'Generate Titles'
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['subroutine']

    if answer == 'Generate Courses':
        from src.openai.generate_courses import main
        main()
    # elif answer == 'Generate Outline':
    #     import src.openai.generate_outlines
    # elif answer == 'Generate Titles':
    #     import src.openai.generate_titles
    else:
        "You did not select a subroutine. Exiting..."

    print('Done.')


if __name__ == '__main__':
    main()
