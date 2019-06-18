from pyspark.sql import DataFrameWriter
import config

class PostgresConnector(object):
    def __init__(self):
        self.hostname = config.POSTGRES_CONFIG['host']
        self.database_name = config.POSTGRES_CONFIG['dbname']
        self.url_connect = "jdbc:postgresql://{hostname}:5432/{db}".format(hostname=self.hostname, db=self.database_name)
        self.properties = {"user":config.POSTGRES_CONFIG['user'],
                      "password":config.POSTGRES_CONFIG['password'],
                      "driver": "org.postgresql.Driver"
                     }

    def get_writer(self, df):
        return DataFrameWriter(df)

    def write(self, df, table, mode):
        my_writer = self.get_writer(df)
        my_writer.jdbc(self.url_connect, table, mode, self.properties)