import airflow
import os, sys

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import date_range

from datetime import datetime, timedelta

default_args = {
                'owner': 'tong_insight',
                'depends_on_past': False,
                'start_date': datetime(2016, 1, 1),
                'end_date': datetime(2016, 12, 31),
                'retries': 2,
                'retry_delay': timedelta(minutes=1),
                }

dag = DAG('wiseLog_dag', default_args = default_args, schedule_interval = timedelta(days=1))
postgres_package = " --packages org.postgresql:postgresql:42.2.5 "
spark_file = "/home/ubuntu/logProcess.py"
data_ingest_file = "/home/ubuntu/dataIngestion.py"

download_data = BashOperator(
                    task_id = "download_data_from_s3",
                    bash_command = "python3 " + data_ingest_file + " {{ ds }}",
                    dag = dag
                    )

spark_master_bp = BashOperator(
                    task_id = "spark_master_batch",
                    bash_command = "/usr/local/spark/bin/spark-submit --master spark://10.0.0.6:7077"
                                   + postgres_package
                                   + spark_file + " {{ ds }}",
                    dag = dag)

spark_master_bp.set_upstream(download_data)
