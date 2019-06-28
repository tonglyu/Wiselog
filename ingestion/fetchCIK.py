import csv
import postgres
import sys
import os
from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.sql import SparkSession

conf = (SparkConf().setAppName("insertCIK")
        .set ( "spark.executor.memory", "4g" )
        .set("spark.dynamicAllocation.enable","true")
        .set("spark.dynamicAllocation.executorIdleTimeout","2m")
        .set("spark.dynamicAllocation.minExecutors",4)
        .set("spark.dynamicAllocation.maxExecutors",2000)
        .set("spakr.stage.maxConsecutiveAttempts",10)
        )
sc = SparkContext(conf = conf)
spark = SparkSession \
    .builder \
    .getOrCreate ()

def write_to_csv(cik_data):
    fieldnames=["cik", "name"]
    with open ( 'cik_company.csv', 'w' ) as csv_file:
        writer = csv.DictWriter ( csv_file, fieldnames=fieldnames )
        writer.writeheader ()
        writer.writerows ( cik_data )

def read_data_url():
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    cik_file = urllib2.urlopen(url)

    cik_data = []
    for line in cik_file:
        ele = line.split(':')
        tmp = {}
        tmp['cik'] = str(ele[1].strip()[3:])
        tmp['name'] = ele[0].strip()
        cik_data.append(tmp)

    return cik_data

def read_csv(file_name):
    schema_list = [
        ('cik', 'STRING'),
        ('name', 'STRING')
    ]
    schema = ", ".join ( ["{} {}".format ( col, type ) for col, type in schema_list] )
    cik_data = sc.textFile(file_name, minPartitions=4)
    header = cik_data.first ()
    new_data = cik_data.filter(lambda line: line != header).map(lambda line: (line.split(',')[0], line.split(',')[1]))\
        .reduceByKey(lambda x,y:x)
    return new_data

def write_to_postgres(out_df, table_name):
    table = table_name
    mode = "append"
    connector = postgres.PostgresConnector()
    connector.write(out_df, table, mode)

if __name__ == '__main__':
    cik_file = sys.argv[1]

    cik_data = read_csv(cik_file)
    print(cik_data.first())
    cik_df = cik_data.toDF(["cik","name"])
    write_to_postgres(cik_df, "cik_company")

    # sql_create_table = """
    #         CREATE TABLE cik_company (
    #             cik TEXT PRIMARY KEY NOT NULL,
    #             name VARCHAR(255) NOT NULL
    #         )
    #         """
    # sql = """
    # INSERT INTO cik_company(cik, name)
    # VALUES(%s, %s)
    # ON CONFLICT (cik) DO NOTHING;"""

    # try:
    #     conn = psycopg2.connect ( database=config.POSTGRES_CONFIG['dbname'], user=config.POSTGRES_CONFIG['user'],
    #                       password=config.POSTGRES_CONFIG['password'], host=config.POSTGRES_CONFIG['host'] )
    #     cur = conn.cursor ()
    #     # print("create table")
    #     # cur.execute ( sql_create_table )
    #     for i in range(len(cik_data)):
    #         print(cik_data[i])
    #         cur.execute ( sql, (cik_data[i]['cik'], cik_data[i]['name']) )
    #         print("insert %d record", i)
    #     cur.close ()
    #     conn.commit()
    # except Exception as er:
    #     print("cannot connect postgres")
    #     print(str ( er ))
    # finally:
    #     if conn is not None:
    #         conn.close ()

    print("finish insert cik table")



