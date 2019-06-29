# Environment Setup
## Install Java 
1. Connect to instances
2. Do all the following for 3 instances. Update configuration     
	```
    sudo apt update
    ```
3. Install jdk
	```
    sudo apt install openjdk-8-jdk
    ```
4. Setting Java-Path
    ```
    vi ~/.bash_profile
    export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
    source ~/.bash_profile
	echo $JAVA_HOME
    ```
## Setting up Python
1. Connect local to EC2
   ```
   chmod 0777 /home/upload #optional
   scp -i YOUR_KEY dataIngestion/dataIngestion.py EC2_DIRECTORY
   ```
2. Install Python and pip
   ```
   sudo apt-get install python3
   python3 --version
   sudo apt install python3-pip
   
   ```
3. Install other command line
   ```
   sudo apt install unzip
   sudo apt install wget
   ```
4. Install AWS cli
   ```
   sudo apt install awscli
   aws configure
   AWS Access Key ID [None]: YOUR_ACCESS_KEY
   AWS Secret Access Key [None]: YOUR_SECRET_KEY
   Default region name [None]: us-west-2
   Default output format [None]: json
   ```

## Setting up passwordless SSH
This allows your machines to ssh into each other without password. Many tools, especially the ones following Master-Worker architecture, require this. Examples: Flink, Spark.      
1. For the master node:    
    ```
    sudo apt install openssh-server openssh-client
    cd ./.ssh/
    ssh-keygen -t rsa -P ""
    ```
    Enter file in which to save the key (/home/ubuntu/.ssh/id_rsa): id_rsa
    Check the id_rsa file
    ```
    cat id_rsa.pub
    ```
2. For other worker nodes:
   ```
   vim ./.ssh/authorized_keys
   ```
   Copy master's SSH key to the second row of configuation files of other nodes.
3. Then, check on master node to see whether other nodes can be connected by
   ```
   ssh -i ~/.ssh/id_rsa ubuntu@PRIVATE_IP  //or
   ssh ubuntu@PRIVATE_IP
   ```

## [Install Spark](https://blog.insightdatascience.com/simply-install-spark-cluster-mode-341843a52b88)
Scala 2.11.12 is better to use with Java8, so donot install Java11.
1. Install scala
   ```
   sudo apt install scala
   scala -version
   ```
   Scala code runner version 2.11.12 -- Copyright 2002-2017, LAMP/EPFL
2. Installing Spark
   ```
   wget http://apache.claz.org/spark/spark-2.4.3/spark-2.4.3-bin-hadoop2.7.tgz
   tar xvf spark-2.4.3-bin-hadoop2.7.tgz
   sudo mv spark-2.4.3-bin-hadoop2.7/ /usr/local/spark
   vi ~/.bash_profile
   export PATH=/usr/local/spark/bin:$PATH
   source ~/.bash_profile
   ```
3. Configuring Master to keep track of its workers (use private ip for each node)
   ```
   vi spark-env.sh
   # contents of conf/spark-env.sh
   export SPARK_MASTER_HOST=MASTER_NODE_PRIVATE_IP
   export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
   vi slaves
   # contents of conf/slaves
   WORKER_NODE1_PRIVATE_IP
   WORKER_NODE2_PRIVATE_IP
   ```
4. Test Running
   ```
   sh /usr/local/spark/sbin/start-all.sh
   sh /usr/local/spark/sbin/stop-all.sh
   ```
5. Edit .bash_profile
   ```
   export PATH=/usr/local/spark/bin:$PATH
   export PYSPARK_PYTHON=python3
   export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
   export PATH=$PATH:$JAVA_HOME/bin
   export AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
   export AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
   ```
* Change host name (NOT SUCCESS)
  ```
  sudo hostnamectl set-hostname NEW_NAME
  sudo vi /etc/hosts
  sudo nano /etc/cloud/cloud.cfg
  ```
  Add 127.0.0.1 NEW_NAME to cloud.cfg
  ```
  hostnamectl
  ```

## Install PostgreSQL
1. Install PostgreSQL
   ```
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo service postgresql 
   ```
2. Log into Postgre user
   ```
   sudo -u postgres -i
   postgres@ip-10-0-0-9:~$ psql
   psql (10.8 (Ubuntu 10.8-0ubuntu0.18.04.1))
   Type "help" for help.
   
   postgres=# 
   ```
3. Configuration
   ```
   cd /etc/postgresql/10/main
   ```
   ```
   vi postgresql.conf

   ...
   listen_addresses = '*' 
   ...
   ```
   ```
   vi pg_hba.conf
   host    all     all     0.0.0.0/0         md5
   ```
   Restart Postrgre!
   ```
   sudo service postgresql restart
   ```
4. Create DB
   ```
   CREATE DATABASE <DB_NAME>;
   CREATE USER <USER_NAME> WITH PASSWORD <PASSWORD>;
   GRANT ALL PRIVILEGES ON DATABASE <DB_NAME> to <USER_NAME>;
   ```
5. Connect to Spark master instance to test whether it is connected.
   ```
   sudo apt-get install postgresql-client
   psql -h <POSTGRE_HOST> -d <DB_NAME> -U <USER_NAME> -p <PORT>
   ```
6. Connect to Spark
   ```
   wget https://jdbc.postgresql.org/download/postgresql-42.2.5.jar
   ```

## [Install Airflow](https://blog.insightdatascience.com/scheduling-spark-jobs-with-airflow-4c66f3144660)
1. Install airflow
   ```
   pip3 install apache-airflow
   vi .bash_profile
   export AIRFLOW_HOME=~/airflow
   export PATH=$PATH:~/.local/bin
   source .bash_profile
   ```
2. Initialising the metadata DB
   ```
   airflow initdb
   ```
3. Make Dag
   ```
   cd airflow/
   mkdir dags
   cd dags
   python3 YOUR_DAG.py
   airflow list_dags 
   ```
4. Start airflow
   ```
   airflow backfill YOUR_DAG_ID -s YYYY-MM-DD
   ```
5. Starting the webserver
   ```
   airflow webserver -p 8082
   ```

## [Install Flask WSGI](https://medium.com/@jQN/deploy-a-flask-app-on-aws-ec2-1850ae4b0d41)
1. Install the apache webserver
   ```
   sudo apt-get update
   sudo apt-get install apache2
   sudo apt-get install libapache2-mod-wsgi-py3
   sudo apt-get install libpq-dev
   ```

2. Install Flask
   ```
   sudo -H pip3 install flask
   mkdir ~/flaskapp
   sudo ln -sT ~/flaskapp /var/www/html/flaskapp
   cd ~/flaskapp
   $ echo "Hello World" > index.html
   ```
3. Running a simple Flask app
   Create flaskapp.py
   ```
   from flask import Flask
   app = Flask(__name__)
   @app.route('/')
   def hello_world():
    return 'Hello from Flask!'
   if __name__ == '__main__':
    app.run()
   ```
   Create a flaskapp.wsgi file to load the app
   ```
   import sys
   sys.path.insert(0, '/var/www/html/flaskapp')
   from flaskapp import app as application
   ```
4. Enable mod_wsgi.
   ```
   sudo vim /etc/apache2/sites-enabled/000-default.conf
   ```
   ```
   WSGIDaemonProcess flaskapp threads=5
   WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi
   <Directory flaskapp>
    WSGIProcessGroup flaskapp
    WSGIApplicationGroup %{GLOBAL}
    Order deny,allow
    Allow from all
   </Directory>
   ```
5. Restart the webserver
   ```
   sudo service apache2 restart
   ```
6. Check the log
   ```
   sudo tail -f /var/log/apache2/error.log
   ```
[Debug Here](https://stackoverflow.com/questions/31252791/flask-importerror-no-module-named-flask)




