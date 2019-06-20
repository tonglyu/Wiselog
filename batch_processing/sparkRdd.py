import sys
import os
import postgres
import config
from geoip2 import database
import geocoder
from pyspark import SparkContext
from pyspark import SparkFiles
from pyspark.sql import (SparkSession,
                         functions as F)

sc = SparkContext(appName="wiseLog")
spark = SparkSession \
    .builder \
    .appName ( "wiseLog" ) \
    .getOrCreate ()

geoDBpath = 'GeoLite2-City.mmdb'
geoPath = os.path.join(geoDBpath)
sc.addFile ( geoPath )

bucket = "loghistory"

def read_csv_from_s3(date):
    '''
    print("start the read csv function:")
    data_file = "log{Date}.csv.gz".format ( Date=self.date )
    s3_bucket = self.bucket

    file_name = "s3a://{bucket}/{file_name}".format ( bucket=s3_bucket, file_name=data_file )

    print('Reading file: ' + file_name)
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
    schema = ", ".join ( ["{} {}".format ( col, type ) for col, type in schema_list] )

    mode = "PERMISSIVE"
    data_file = "log{Date}.csv.gz".format ( Date= date )
    file_name = "s3a://{bucket}/{file_name}".format ( bucket=bucket, file_name=data_file )
    return spark.read.csv ( file_name, header=True, mode=mode, schema=schema )

def format_dataframe(csv_df):
    col_select = ("ip","date","cik")
    df = csv_df.select ( *col_select )
    df.createOrReplaceTempView ( "table" )

    format_ip = F.udf(lambda ip: ip[:-4] + '.0')
    df = df.withColumn('ip', format_ip('ip'))
    format_cik = F.udf(lambda cik: cik[:-2])
    df = df.withColumn('cik', format_cik('cik'))
    '''
    df = df.withColumn ( 'hour', F.hour ( df['time'] ) )
    df = df.withColumn ( 'minute', F.minute ( df['time'] ) )
    df = df.withColumn ( 'second', F.second ( df['time'] ) )
    '''
    return df


def write_to_postgres(out_df, table_name):
    table = table_name
    mode = "append"
    connector = postgres.PostgresConnector()
    connector.write(out_df, table, mode)

def partitionIp2city(iter):
    def ip2city(ip):
        try:
            match = reader.city (ip)
            # res = []
            # res.append(match.continent.code)
            # res.append(match.country.iso_code)
            # res.append(match.subdivisions.most_specific.iso_code)
            # res.append(match.city.name)
            #return match.country.iso_code,match.subdivisions.most_specific.iso_code,match.city.name, 
            return match.city.geoname_id
        except:
            res = 'not found'
            return res
    print("Begin ip 2 city")
    geoRdd = []
    reader = database.Reader ( SparkFiles.get (geoDBpath ) )
    for line in iter:
        #(ip, cik), count -> cik, (country, region, city, )geoname_id, count
        ip_tuple = ((line[0][1], ip2city(line[0][0])), line[1])
        geoRdd.append(ip_tuple)
    return geoRdd

def cal_coordinate(geoname_id):
    res = geocoder.geonames(geoname_id, method='details',key=config.GEOCODER['username'])
    return res.lat, res.lng


def run(date):
    date = "".join ( date.split ( "-" ) )
    print("batch_run_date: ", date)

    csv_df = read_csv_from_s3 (date)

    format_df = format_dataframe ( csv_df )
    format_df.show()

    format_rdd = format_df.rdd.map ( tuple )
    #(ip, cik), 1
    geo_ori_rdd = format_rdd.map(lambda rec: ((rec[0], rec[2]),1))\
        .reduceByKey ( lambda a, b: a + b , 10)
    print(geo_ori_rdd.first())
    # (cik, country, region, city, geoname_id), count
    geo_rdd = geo_ori_rdd.mapPartitions ( partitionIp2city )\
        .filter(lambda tuple: tuple[0][1] is not None)\
        .reduceByKey(lambda a, b: a + b)\
        .map(lambda line: (line[0][0], line[0][1], line[1]))

    geo_df = geo_rdd.toDF( ['cik', 'geoname_id', 'count'])
    geo_df.show()

    print("Saving top company table into Postgres...")
    write_to_postgres ( geo_df, "company_geo_" + date )
    '''
    ## average
    RDD1 = self.mapRdd ( format_df )
    RDD1 = RDD1.reduceByKey ( func )

    ave_df = RDD1.map ( lambda x: [x[0][0], x[0][1], x[1][0], x[1][1], x[1][2]] ) \
        .toDF ( ['ip', 'hour_session', 'min', 'max', 'count'] )
    ave_df.show ()

    ## top company
    RDD2 = self.comp_top_company ( format_df )
    top_df = RDD2.map ( lambda x: [x[0][0], x[0][1], x[1]] ) \
        .toDF ( ['hour_session', 'company_id', 'count'] )
    top_df.show ()

    print("Saving average table into Postgres...")
    self.write_to_postgres(ave_df, "ave_tab_" + date)

    
    '''
    print("Batch process finished.")

def main():
    date = sys.argv[1]
    run(date)


main ()

def func(tuple1, tuple2):
    """
    reduceByKey function
    """

    if tuple2[0] <= tuple1[0]:
        return (tuple2[0], tuple1[1], tuple1[2] + 1)
    else:
        if tuple2[0] > tuple1[1]:
            return (tuple1[0], tuple2[0], tuple1[2] + 1)
        else:
            return (tuple1[0], tuple1[1], tuple1[2] + 1)


def comp_top_company(df):
    df = df.withColumn ( 'Company_ID', F.substring ( 'accession', pos=0, len=10 ) )
    print(df.printSchema ())
    myRDD = df.rdd.map ( tuple )
    myRDD = myRDD.map ( lambda x: ((x[4], x[7], x[0]), 1) ) \
        .reduceByKey ( lambda a, b: a + b ) \
        .map ( lambda x: ((x[0][0], x[0][1]), 1) ) \
        .reduceByKey ( lambda a, b: a + b )

    return myRDD

