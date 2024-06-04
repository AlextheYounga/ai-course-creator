import sys
import inquirer
from termcolor import colored
from db.db import DB, JobStore

db = DB()


def select_jobstore():
    job_records = db.query(JobStore).order_by(
        JobStore.id.desc()
    ).all()

    if len(job_records) == 0:
        print(colored("No jobs found. Exiting...", "red"))
        sys.exit()

    job_mapping = [
        {'name': f"{job.name} - {job.created_at}", 'id': job.id}
        for job in job_records
    ]

    job_mapping[0]['name'] = f"{job_mapping[0]['name']} (latest)"
    job_names = [job['name'] for job in job_mapping]

    job_select = [
        inquirer.List('jobSelect',
                      message=f"Select job",
                      choices=job_names),
    ]

    user_prompt = inquirer.prompt(job_select, raise_keyboard_interrupt=True)

    if user_prompt != None:
        answer = user_prompt['jobSelect']

        selected_job = [
            obj for obj in job_mapping
            if obj['name'] == answer
        ][0]

        for record in job_records:
            if record.id == selected_job['id']:
                return record

        raise Exception("You did not select a job. Exiting...")
