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
                'end_date': datetime(2017, 5, 31),
                'retries': 5,
                'retry_delay': timedelta(minutes=1),
                }

dag = DAG('wiseLog_dag', default_args = default_args, schedule_interval = timedelta(days=1))
configuration = " --conf \"spark.default.parallelism=24\" --conf \"spark.dynamicAllocation.enable = true\" --conf \"spark.dynamicAllocation.executorIdleTimeout = 2m\" --conf \"spark.dynamicAllocation.minExecutors = 1\" --conf \"spark.dynamicAllocation.maxExecutors = 2000\" --conf \"spakr.stage.maxConsecutiveAttempts = 10\" --conf \"spark.memory.offHeap.enable = true\" --conf \"spark.memory.offheep.size = 3g\" --conf \"spark.yarn.executor.memoryOverhead = 0.1 * (spark.executor.memory + spark.memory.offHeap.size)\""
# postgres_package = " --packages org.postgresql:postgresql:42.1.1 "
spark_file = "/home/ubuntu/batch_process.py"
data_ingest_file = "/home/ubuntu/dataIngestion.py"

download_data = BashOperator(
                    task_id = "download_data_from_s3",
                    bash_command = "python3 " + data_ingest_file + " {{ ds }}",
                    dag = dag
                    )

spark_master_bp = BashOperator(
                    task_id = "spark_master_batch",
                    bash_command = "spark-submit --master spark://10.0.0.5:7077" \
                                   + configuration
                                   + spark_file + " {{ ds }}",
                    dag = dag)

spark_master_bp.set_upstream(download_data)
