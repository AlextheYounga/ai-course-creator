import inquirer


def main():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=[
                          'Generate Courses',
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['subroutine']

    if answer == 'Generate Courses':
        from src.openai.course_creator import run
        run()
    else:
        "You did not select a subroutine. Exiting..."

    print('Done.')


if __name__ == '__main__':
    main()
