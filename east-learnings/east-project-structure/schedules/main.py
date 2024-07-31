from dagster import ScheduleDefinition, job, schedule


@job(name="main_job")
def main_job():
    print("Hello, World!")

@schedule(job_name="main_job", cron_schedule="0 0 * * *")
def main_cron():
    print("Hello, World!")

