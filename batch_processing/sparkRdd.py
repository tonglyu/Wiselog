from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("wiselog").setMaster("local[2]")
sc = SparkContext(conf=conf)

log_file = sc.textFile("../log20170630.csv.gz")
header = log_file.first()
# (ip, date, time, cik)
log_rdd = log_file.filter(lambda line: line != header).map(lambda line:
                                 (line.split(",")[0], line.split(",")[1], line.split(",")[2], int(float(line.split(",")[4]))))\
    .map(lambda line: (line[0], line[1], int(line[2].split(":")[0]), line[3]))

company_rdd = log_rdd.map(lambda line: ((line[2], line[3], line[0]), 1))\
    .reduceByKey(lambda x,y: x + y)\
    .map(lambda line: ((line[0][0], line[0][1]),1))\
    .reduceByKey(lambda x,y: x + y)\
    .map(lambda line: [line[0][0], line[0][1], line[1]])

company_df = company_rdd.toDF(['hour_session', 'company_id', 'count'])


company_df.show()

