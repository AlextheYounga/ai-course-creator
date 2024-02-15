from db.db import DB, Page
from termcolor import colored



def add_headers_to_all_pages():
    pages = DB.query(Page).filter(Page.type == 'page').all()

    for page in pages:
        content = page.content
        if content:
            # If header is h1, skip
            if content[:2] == '# ': continue

            # If header is h2, make h1
            if content[:3] == '## ':
                split_content = content.split('## ', 1)[1]
                content = '# ' + split_content

            # If header is h3, make h1
            if content[:3] == '### ':
                split_content = content.split('## ', 1)[1]
                content = '# ' + split_content

            if content[:2] != '# ':
                header = f"# {page.name}\n"
                content = header + content

            print(colored(content.split('\n')[0] + "\n", "green"))

            page.content = content
            DB.commit()


def add_headers_to_all_challenges():
    pages = DB.query(Page).filter(Page.type == 'challenge').all()

    for page in pages:
        content = page.content
        if content:
            # If header is h1, skip
            if content[:2] == '# ': continue

            # If header is h2, make h1
            if content[:3] == '## ':
                split_content = content.split('## ', 1)[1]
                content = '# ' + split_content

            # If header is h3, make h1
            if content[:3] == '### ':
                split_content = content.split('## ', 1)[1]
                content = '# ' + split_content

            if content[:2] != '# ':
                header = "# Practice Skill Challenge\n"
                content = header + content

            print(colored(content.split('\n')[0] + "\n", "green"))

            page.content = content
            DB.commit()


def add_headers_to_all_fsc():
    pages = DB.query(Page).filter(Page.type == 'final-skill-challenge').all()

    for page in pages:
        content = page.content
        if page.name == 'Final Skill Challenge Page 1' and content:
            # If header is h1, skip
            if content[:2] == '# ': continue

            # If header is h2, make h1
            if content[:3] == '## ':
                split_content = content.split('## ', 1)[1]
                content = '# ' + split_content

            # If header is h3, make h1
            if content[:3] == '### ':
                split_content = content.split('## ', 1)[1]
                content = '# ' + split_content

            if content[:2] != '# ':
                header = "# Final Skill Challenge\n"
                content = header + content

            print(colored(content.split('\n')[0] + "\n", "green"))

            page.content = content
            DB.commit()


add_headers_to_all_pages()
add_headers_to_all_challenges()
add_headers_to_all_fsc()
