from pyspark import SparkContext, SparkConf
from pyspark.sql.types import StringType
from pyspark import SparkFiles
from geoip2 import database
import os

from pyspark.sql import (SparkSession,
                         functions as F)


sc = SparkContext(appName="wiseLog")
spark = SparkSession \
    .builder \
    .appName ( "wiseLog" ) \
    .getOrCreate ()

geoDBpath = os.path.join ( 'GeoLite2-City.mmdb' )
sc.addFile ( geoDBpath )

date = '2017-06-03'
bucket = "loghistory"

def read_csv_from_s3():
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
    file_name = "../log20170630(start2).csv"
    return spark.read.csv ( file_name, header=True, mode=mode, schema=schema )

def manipulate_df(csv_df):
    col_select = ("ip",
                       "date",
                       "time",
                       "cik"
                       )
    df = csv_df.select ( *col_select )
    df.createOrReplaceTempView ( "table" )
    df = df.withColumn ( 'hour', F.hour ( df['time'] ) )
    trans_ip = F.udf(lambda ip: ip[:-4] + '.0')
    df = df.withColumn('ip', trans_ip('ip'))
    '''
    df = df.withColumn ( 'minute', F.minute ( df['time'] ) )
    df = df.withColumn ( 'second', F.second ( df['time'] ) )
    '''
    return df


def write_to_postgres(self, out_df, table_name):
    table = table_name
    mode = "append"
    # connector = postgres.PostgresConnector()
    # connector.write(out_df, table, mode)

def partitionIp2city(iter):
    def ip2city(ip):
        try:
            match = reader.city (ip)
            res = []
            res.append(match.continent.code)
            res.append(match.country.iso_code)
            res.append(match.subdivisions.most_specific.iso_code)
            res.append(match.city.name)
            return match.continent.code,match.country.iso_code,match.subdivisions.most_specific.iso_code,match.city.name
        except:
            res = 'not found'
            return res
    geoRdd = []
    reader = database.Reader ( SparkFiles.get (geoDBpath ) )
    for line in iter:
        ip_tuple = (line[0][0], line[0][1], ip2city(line[0][1]), line[1])
        geoRdd.append(ip_tuple)
    return geoRdd



def run(date):
    date = "".join ( date.split ( "-" ) )
    print("batch_run_date: ", date)

    csv_df = read_csv_from_s3 ()

    out_df = manipulate_df ( csv_df )
    out_df.printSchema ()

    out_rdd = out_df.rdd.map ( tuple )
    geo_ori_rdd = out_rdd.map(lambda rec: ((rec[4], rec[0]),1))\
        .reduceByKey ( lambda a, b: a + b )

    geo_rdd = geo_ori_rdd.mapPartitions ( partitionIp2city )\
        .map(lambda rec: (rec[0], rec[1], rec[2][0],rec[2][1],rec[2][2],rec[2][3],rec[3]))

    geo_df = geo_rdd.toDF( ['hour_session', 'ip','continent','country','region','city','count'])
    geo_df.show()
    '''
    ## average
    RDD1 = self.mapRdd ( out_df )
    RDD1 = RDD1.reduceByKey ( func )

    ave_df = RDD1.map ( lambda x: [x[0][0], x[0][1], x[1][0], x[1][1], x[1][2]] ) \
        .toDF ( ['ip', 'hour_session', 'min', 'max', 'count'] )
    ave_df.show ()

    ## top company
    RDD2 = self.comp_top_company ( out_df )
    top_df = RDD2.map ( lambda x: [x[0][0], x[0][1], x[1]] ) \
        .toDF ( ['hour_session', 'company_id', 'count'] )
    top_df.show ()

    print("Saving average table into Postgres...")
    self.write_to_postgres(ave_df, "ave_tab_" + date)

    print("Saving top company table into Postgres...")
    self.write_to_postgres(top_df, "top_tab_" + date)
    '''
    print("Batch process finished.")

def main():

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

def mapRdd(df):
    ### map - (ip, hour session) -> (minute, second)
    ### map - (ip, hour session) -> seconds
    ### map - (ip, hour session) -> (seconds, 0, 0)  --  minimun, maximum, count
    myRDD = df.rdd.map ( tuple )
    myRDD = myRDD.map ( lambda x: ((x[0], x[4]), (x[5], x[6])) ) \
        .map ( lambda x: (x[0], x[1][0] * 60 + x[1][1]) ) \
        .map ( lambda x: (x[0], (x[1], 0, 0)) )
    return myRDD

def comp_top_company(df):
    df = df.withColumn ( 'Company_ID', F.substring ( 'accession', pos=0, len=10 ) )
    print(df.printSchema ())
    myRDD = df.rdd.map ( tuple )
    myRDD = myRDD.map ( lambda x: ((x[4], x[7], x[0]), 1) ) \
        .reduceByKey ( lambda a, b: a + b ) \
        .map ( lambda x: ((x[0][0], x[0][1]), 1) ) \
        .reduceByKey ( lambda a, b: a + b )

    return myRDD
'''
conf = SparkConf().setAppName("wiselog").setMaster("local[2]")
sc = SparkContext(conf=conf)
spark = SparkSession(sc)

log_file = sc.textFile("../log20170630(start2).csv")
header = log_file.first()
# (ip, date, time, cik)
log_rdd = log_file.filter(lambda line: line != header)
print(log_rdd.first().split(","))
log_rdd =  log_rdd.map(lambda line:(line.split(",")[0], line.split(",")[1], line.split(",")[2]))\
    .map(lambda line: (line[0], line[1], int(line[2].split(":")[0])))



loc_rdd = log_rdd.map(lambda line: ((line[2], line[0]), 1))\
    .reduceByKey(lambda x,y: x + y)\
    .map(lambda line: (line[0][0], geoLoc(line[0][1]), line[1]))

print(loc_rdd.first())
# loc_df = loc_rdd.toDF(['hour','continent','country','region','city','count'])
# loc_df.show()

company_rdd = log_rdd.map(lambda line: ((line[2], line[3], line[0]), 1))\
    .reduceByKey(lambda x,y: x + y)\
    .map(lambda line: ((line[0][0], line[0][1]),1))\
    .reduceByKey(lambda x,y: x + y)\
    .map(lambda line: [line[0][0], line[0][1], line[1]])





company_df = company_rdd.toDF(['hour_session', 'company_id', 'count'])
match = geolite2.lookup

company_df.show()
'''

