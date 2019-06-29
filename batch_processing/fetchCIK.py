import urllib2
import csv
import postgres
import sys
from pyspark import SparkContext, SparkConf
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
        writer = csv.DictWriter ( csv_file, fieldnames=fieldnames, delimiter=':')
        writer.writeheader ()
        writer.writerows ( cik_data )

def read_data_url():
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    cik_file = urllib2.urlopen(url)

    cik_data = []
    for line in cik_file:
        ele = line.split(':')
        tmp = {}
        tmp['cik'] = str(ele[1].strip().lstrip('0'))
        name = ele[0].strip().strip('"')
        if name.startswith ( '"' ) and name.endswith ( '"' ):
            name = name[1:-1]
        tmp['name'] = name
        cik_data.append(tmp)

    return cik_data

def url2csv():
    cik_data = read_data_url()
    write_to_csv(cik_data)

def read_csv(file_name):
    schema_list = [
        ('cik', 'STRING'),
        ('name', 'STRING')
    ]
    schema = ", ".join ( ["{} {}".format ( col, type ) for col, type in schema_list] )
    mode = "PERMISSIVE"
    cik_data = spark.read.csv ( file_name, header=True, mode=mode, schema=schema )
    #deduplication
    new_data = cik_data.rdd.map ( tuple )\
        .reduceByKey(lambda x,y:x)
    return new_data

def write_to_postgres(out_df, table_name):
    table = table_name
    mode = "append"
    connector = postgres.PostgresConnector()
    connector.write(out_df, table, mode)

if __name__ == '__main__':
    # Get original data and save
    # url2csv()

    cik_file = sys.argv[1]
    cik_data = read_csv(cik_file)
    cik_df = cik_data.toDF(["cik","name"])

    #Save to DB
    write_to_postgres(cik_df, "cik_company")

    print("finish insert cik table")



