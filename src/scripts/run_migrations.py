from termcolor import colored


def add_outline_chunks():
    print(colored("Migrating add_outline_chunks_to_outline...", "yellow"))
    from db.migrations.add_outline_chunks_to_outline import up
    up()
    print(colored("Done.", "green"))


def run_db_migrations():
    add_outline_chunks()
