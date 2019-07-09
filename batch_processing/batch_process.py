import os
import sys

from geoip2 import database
from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.sql import (SparkSession,
                         functions as F)
import postgres

conf = SparkConf().setAppName("wiseLog") \
        .set ( "spark.executor.memory", "4g" ) \
        .set("spark.default.parallelism",30)

sc = SparkContext(conf = conf)
spark = SparkSession \
    .builder \
    .getOrCreate ()

geoDBpath = 'GeoLite2-City.mmdb'
geoPath = '/home/ubuntu/' + geoDBpath
sc.addFile ( geoPath )

bucket = "loghistory"

def read_csv_from_s3(date):
    '''
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
    '''
    file_name = "log{Date}.csv.gz".format ( Date= date )
    file_zip = "s3a://{bucket}/{file_name}".format ( bucket=bucket, file_name= file_name )
    file_data = sc.textFile(file_zip)
    header = file_data.first()

    # (ip, cik), 1 --> (ip, cik, count)
    def format(line):
        ele = line.split(',')
        ip = ele[0][:-4] + '.0'
        cik = ele[4][:-2]
        acc = ele[5].split('-')[0].lstrip('0')
        if len(cik) > 7:
            cik = acc
        return (ip , cik), 1

    new_data = file_data.filter(lambda line: line != header)\
        .map(lambda line: (format(line)))\
        .reduceByKey(lambda a,b: a + b)
    return new_data

def partitionIp2city(iter):
    def ip2city(ip):
        try:
            match = reader.city (ip)
            return match.city.geoname_id
        except:
            return None
    geo_rdd = []
    reader = database.Reader ( SparkFiles.get (geoDBpath ) )
    for line in iter:
        #(ip, cik), count -> cik, geoname_id, count
        ip_tuple = ((line[0][1], ip2city(line[0][0])), line[1])
        geo_rdd.append(ip_tuple)
    return geo_rdd

def write_to_postgres(out_df, table_name):
    table = table_name
    mode = "append"
    connector = postgres.PostgresConnector()
    connector.write(out_df, table, mode)

def run(date, geolite_file):
    date_format = "".join ( date.split ( "-" ) )
    print("Batch_run_date: ", date)

    print("******************************* Begin reading data *******************************\n")
    # Geolocation table ("geoname_id", "country_iso_code")
    col_select = ("geoname_id", "country_iso_code")
    geolite_df = spark.read.csv ( geolite_file, header=True, mode= "PERMISSIVE" )
    geolite_df = geolite_df.select(*col_select)
    # Log file table
    ip_cik_rdd = read_csv_from_s3 ( date_format )


    print("******************************* Begin ip 2 city *******************************\n")
    # (cik, geoname_id), count
    geo_rdd = ip_cik_rdd.mapPartitions ( partitionIp2city ) \
        .filter ( lambda tuple: tuple[0][1] is not None ) \
        .reduceByKey ( lambda a, b: a + b) \
        .map ( lambda line: (date, line[0][0], line[0][1], line[1]) )
    geo_df = geo_rdd.toDF(["date", "cik","geoname_id","count"])

    print("******************************* Begin join country code *******************************\n")
    city_df = geo_df.join(F.broadcast(geolite_df), ["geoname_id"])
    city_df.select("date", "cik", "count", "country_iso_code","geoname_id")
    city_df.show()


    print("******************************* Saving company table into Postgres *******************************\n")
    write_to_postgres ( city_df, "log_geolocation")

    print("******************************* Batch process finished. *******************************\n")

if __name__ == '__main__':
    date = sys.argv[1]
    geolite_file = "s3a://{bucket}/{file_name}".format ( bucket=bucket, file_name= "GeoLite2-City-Locations-en.csv" )
    run ( date, geolite_file )