import subprocess
import sys

class DataIngestion(object):
    def __init__(self, date):

        """
        Input: date of data that want to process
        Input Type: String
        Input Format: "yyyy-mm-dd"
        """

        self.date = "".join(date.split("-")) # "yyyy-mm-dd" -> "yyyymmdd"
        self.bucket = "loghistory"

        ## split the date string into year, month, day string format

        self.year = date.split("-")[0]
        self.month = date.split("-")[1]
        self.day = date.split("-")[2]

        self.qtr = int(self.month)//4 + 1
        self.src_link = "http://www.sec.gov/dera/data/Public-EDGAR-log-file-data/{Year}/Qtr{Quarter}/log{Date}.zip" \
                        .format(Year = self.year, Quarter = str(self.qtr), Date = self.date)
        self.data_file = "log{Date}.csv.gz".format(Date = self.date)

    def import_data_to_S3(self):

        """
        Download the data file from the website;
        Save it temporarily on machine and extract .csv file;
        Gzip .csv file and import into S3;
        Delete readme.txt and .zip file;
        Return the gzipped file name;
        """

        subprocess.run(["wget", self.src_link])
        zipfile = "log{Date}.zip".format(Date = self.date)
        csvfile = "log{Date}.csv".format(Date = self.date)
        subprocess.run(["unzip", zipfile])
        subprocess.run(["rm", zipfile])
        subprocess.run(["rm", "README.txt"])
        subprocess.run(["gzip", csvfile])
        gzfile = "log{Date}.csv.gz".format(Date = self.date)
        subprocess.run(["aws", "s3", "cp", gzfile, "s3://{Bucket}/".format(Bucket = self.bucket)])
        subprocess.run(["rm", gzfile])

    def run(self):
        self.import_data_to_S3()
        print("Finish importing data to S3!")

def main():
    date = sys.argv[1]
    proc = DataIngestion(date)
    proc.run()

main()