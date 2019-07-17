import sys

from geoip2 import database
from pyspark import SparkFiles
from pyspark.sql import (SparkSession,functions as F)

import dbConnector


spark = SparkSession.builder\
    .appName ( "wiseLog" )\
    .config("spark.executor.memory", "4g")\
    .config("spark.sql.shuffle.partitions",30)\
    .config("spark.default.parallelism",30)\
    .getOrCreate ()


sc = spark.sparkContext

geoDBpath = 'GeoLite2-City.mmdb'
geoPath = '/home/ubuntu/' + geoDBpath
sc.addFile ( geoPath )

bucket = "loghistory"

def read_csv_from_s3(date):
    schema_list = [
        ('ip', 'STRING'),
        ('date', 'STRING'),
        ('time', 'STRING'),
        ('zone', 'STRING'),
        ('cik', 'STRING'),
        ('accession', 'STRING'),
        ('extention', 'STRING'),
        ('code', 'STRING'),
        ('size', 'STRING'),
        ('idx', 'STRING'),
        ('norefer', 'STRING'),
        ('noagent', 'STRING'),
        ('find', 'STRING'),
        ('crawler', 'STRING'),
        ('browser', 'STRING')
    ]
    schema = ", ".join ( ["{} {}".format ( col, type ) for col, type in schema_list] )
    file_name = "log{Date}.csv.gz".format ( Date= date )
    file_zip = "s3a://{bucket}/{file_name}".format ( bucket=bucket, file_name= file_name )
    mode = "PERMISSIVE"

    return spark.read.csv ( file_zip, header=True, mode=mode, schema=schema )

def format_dataframe(csv_df):
    col_select = ("ip","cik","accession")
    df = csv_df.select ( *col_select )
    df.createOrReplaceTempView ( "table" )

    format_ip = F.udf(lambda ip: ip[:-4] + '.0')
    df = df.withColumn('ip', format_ip('ip'))

    format_acc = F.udf(lambda acc: acc.split('-')[0].lstrip('0'))
    df = df.withColumn ( 'accession', format_acc('accession') )

    def helper(cik, acc):
        cik = cik[:-2]
        if len(cik) > 7:
            return acc
        else:
            return cik
    format_cik = F.udf(lambda cik, acc: helper(cik, acc))
    df = df.withColumn('cik', format_cik(F.col('cik'),F.col('accession'))).drop('accession')
    return df

def partitionIp2city(iter):
    def ip2city(ip):
        try:
            match = reader.city (ip)
            return match.city.geoname_id
        except:
            return None
    geo_df = []
    reader = database.Reader ( SparkFiles.get (geoDBpath ) )
    for line in iter:
        print(line)
        #(ip, cik), count -> (cik, geoname_id), count
        ip_tuple = (line[1], ip2city(line[0]), line[2])
        geo_df.append(ip_tuple)
    return geo_df

def write_to_postgres(out_df, table_name):
    table = table_name
    mode = "append"
    connector = dbConnector.PostgresConnector()
    connector.write(out_df, table, mode)

def run(date, geolite_file):
    date_format = "".join ( date.split ( "-" ) )
    print("Batch_run_date: ", date)

    print("******************************* Begin reading data *******************************\n")
    #Geolocation table ("geoname_id", "country_iso_code")
    col_select = ("geoname_id", "country_iso_code")
    geolite_df = spark.read.csv ( geolite_file, header=True, mode= "PERMISSIVE" )
    geolite_df = geolite_df.select(*col_select)

    #Log file table
    csv_df = read_csv_from_s3 ( date_format )
    ip_cik_format_df = format_dataframe ( csv_df )
    ip_cik_format_df.createOrReplaceTempView ( "ip_cik_table" )
    ip_cik_df = spark.sql("SELECT ip, cik , count(*) AS count FROM ip_cik_table GROUP BY ip, cik")

    print("******************************* Begin ip 2 city *******************************\n")
    # (cik, geoname_id), count
    cik_geo_df = ip_cik_df.rdd.mapPartitions ( partitionIp2city ).toDF(["cik","geoname_id","count"])
    cik_geo_df = cik_geo_df.filter ( "geoname_id is not null")
    cik_geo_df.show()
    cik_geo_df.createOrReplaceTempView ( "cik_geo_table" )
    cik_geo_agg_df = spark.sql("SELECT cik, geoname_id, sum(count) AS count FROM cik_geo_table GROUP BY cik, geoname_id")
    cik_geo_agg_df = cik_geo_agg_df.withColumn ( 'date', F.lit(date))

    print("******************************* Begin calculate coordinates *******************************\n")
    # (cik, geoname_id, date, count) -> (date, cik, geoname_id, country_iso_code, count)
    city_df = cik_geo_agg_df.join(F.broadcast(geolite_df), ["geoname_id"])
    city_df.select("date", "cik", "count", "country_iso_code","geoname_id")
    city_df.show()

    print("******************************* Saving company table into Postgres *******************************\n")
    write_to_postgres ( city_df, "log_geolocation")

    print("******************************* Batch process finished. *******************************\n")

if __name__ == '__main__':
    date = sys.argv[1]
    geolite_file = "s3a://{bucket}/{file_name}".format ( bucket=bucket, file_name= "GeoLite2-City-Locations-en.csv" )
    run ( date, geolite_file )