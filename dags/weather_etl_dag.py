from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'you',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='weather_etl',
    default_args=default_args,
    description='Hourly weather ELT',
    schedule_interval='@hourly',  # Runs every hour
    start_date=datetime(2026, 6, 1),
    catchup=False,
) as dag:

    extract = BashOperator(
        task_id='extract_weather',
        bash_command='python /opt/airflow/local/extract.py',
    )

    load = BashOperator(
        task_id='load_to_postgres',
        bash_command='python /opt/airflow/local/load.py',
    )

    extract >> load  