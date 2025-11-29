from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.sns import SnsPublishOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:airflow-alerts"


def task_failure_alert(context):
    task_id = context.get("task_instance").task_id
    dag_id = context.get("dag").dag_id
    msg = f"Glue Job FAILED → DAG={dag_id}, Task={task_id}"
    SnsPublishOperator(
        task_id="failure_sns_alert",
        target_arn=SNS_TOPIC_ARN,
        message=msg
    ).execute(context=context)


default_args = {
    "owner": "autosys_migration",
    "email_on_failure": True,
    "email": ["etl-alerts@bank.com"],
    "retry_delay": timedelta(minutes=5),
    "retries": 1,
}

with DAG(
    dag_id="parallel_autosys_chain",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["autosys", "glue", "parallel"]
) as dag:

    file_sensor = S3KeySensor(
        task_id="FILE_WATCHER",
        bucket_name="bank-etl-input",
        bucket_key="incoming/events.csv",
        aws_conn_id="aws_default",
        poke_interval=60,
        timeout=3600,
        mode="poke",
    )

    JOB1 = GlueJobOperator(
        task_id="JOB1",
        job_name="glue_job1",
        script_location="s3://bank-etl/scripts/job1.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
        on_failure_callback=task_failure_alert,
    )

    JOB2 = GlueJobOperator(
        task_id="JOB2",
        job_name="glue_job2",
        script_location="s3://bank-etl/scripts/job2.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
        on_failure_callback=task_failure_alert,
    )

    JOB3 = GlueJobOperator(
        task_id="JOB3",
        job_name="glue_job3",
        script_location="s3://bank-etl/scripts/job3.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
        trigger_rule=TriggerRule.ALL_SUCCESS,
        on_failure_callback=task_failure_alert,
    )

    file_sensor >> [JOB1, JOB2]
    [JOB1, JOB2] >> JOB3

    JOB4 = GlueJobOperator(
        task_id="JOB4",
        job_name="glue_job4",
        script_location="s3://bank-etl/scripts/job4.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
    )

    JOB5 = GlueJobOperator(
        task_id="JOB5",
        job_name="glue_job5",
        script_location="s3://bank-etl/scripts/job5.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
    )

    JOB6 = GlueJobOperator(
        task_id="JOB6",
        job_name="glue_job6",
        script_location="s3://bank-etl/scripts/job6.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
    )

    [JOB4, JOB5, JOB6]

    JOB7 = GlueJobOperator(
        task_id="JOB7",
        job_name="glue_job7",
        script_location="s3://bank-etl/scripts/job7.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    [JOB5, JOB6] >> JOB7

    JOB8 = GlueJobOperator(
        task_id="JOB8",
        job_name="glue_job8",
        script_location="s3://bank-etl/scripts/job8.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
    )

    JOB7 >> JOB8

    JOB9 = GlueJobOperator(
        task_id="JOB9",
        job_name="glue_job9",
        script_location="s3://bank-etl/scripts/job9.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
    )

    JOB10 = GlueJobOperator(
        task_id="JOB10",
        job_name="glue_job10",
        script_location="s3://bank-etl/scripts/job10.py",
        region_name="us-east-1",
        iam_role_name="Glue_ETL_Job_Role",
        aws_conn_id="aws_default",
    )

    JOB8 >> [JOB9, JOB10]
