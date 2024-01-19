import inquirer
from src.scripts.run_all import run_all


def select_subroutine():
    choices = [
        inquirer.List('subroutine',
                      message="Select subroutine.",
                      choices=[
                          'Generate Course Outlines',
                          'Generate Course Pages',
                          'Generate Practice Skill Challenges',
                          'Generate Final Skill Challenges',
                          'Run All',
                      ]),
    ]

    choice = inquirer.prompt(choices)
    answer = choice['subroutine']

    if answer == 'Generate Course Outlines':
        from src.openai.outlines.create_outlines import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Generate Course Pages':
        from src.openai.page_material_creator import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Generate Practice Skill Challenges':
        from src.openai.practice_skill_challenge_creator import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Generate Final Skill Challenges':
        from src.openai.final_skill_challenge_creator import cli_prompt_user
        cli_prompt_user()
    elif answer == 'Run All':
        run_all()

    else:
        "You did not select a subroutine. Exiting..."