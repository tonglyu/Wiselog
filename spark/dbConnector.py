from pyspark.sql import DataFrameWriter
import config

class PostgresConnector(object):
    def __init__(self):
        self.host = config.POSTGRES_CONFIG['host']
        self.port = config.POSTGRES_CONFIG['port']
        self.database = config.POSTGRES_CONFIG['dbname']
        self.url_connect = "jdbc:postgresql://{host}:{port}/{db}".format(host=self.host, port=self.port, db=self.database)
        self.properties = {"user":config.POSTGRES_CONFIG['user'],
                      "password":config.POSTGRES_CONFIG['password'],
                      "driver": "org.postgresql.Driver"
                     }

    def get_writer(self, df):
        return DataFrameWriter(df)

    def write(self, df, table, mode):
        my_writer = self.get_writer(df)
        my_writer.jdbc(self.url_connect, table, mode, self.properties)

    def loadFromPostGres(self, spark, name):
        df = spark.read.jdbc ( url=self.url_connect, table=name, properties=self.properties )
        return df