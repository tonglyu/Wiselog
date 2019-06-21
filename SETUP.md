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

## Install Kafka Cluster
Set new EC2 instances, set up environments including:
   * Passwordless SSH
   * Java 8
   * Scala 2.11.12     

### [Zookeeper](https://www.cnblogs.com/wxisme/p/5178211.html)
1. Download zookeeper
   ```
   wget https://archive.apache.org/dist/zookeeper/zookeeper-3.4.12/zookeeper-3.4.12.tar.gz  
   tar -xvzf zookeeper-3.4.12.tar.gz
   ```
2. Navigate to the ZooKeeper properties file (/conf/zoo.cong) file and modify as shown.
   Set 0.0.0.0 for current node, and private ip for other nodes
   ```
    tickTime=2000
    dataDir=/var/lib/zookeeper
    clientPort=2181
    initLimit=5
    syncLimit=2
    server.1=0.0.0.0:2888:3888    #ZOOKEEPER_NODE1(corresponding to myid)
    server.2=ZOOKEEPER_NODE2_PRIVATE_IP:2888:3888  #private_ip of EC2
    server.3=ZOOKEEPER_NODE3_PRIVATE_IP:2888:3888
    autopurge.snapRetainCount=3
    autopurge.purgeInterval=24
   ```
3. Change myid file
   ```
   mkdir /var/lib/zookeeper  #keep same with dataDir
   chmod 755 /var/lib/zookeeper #optional in case of permission problem
   chown USER_NAME /var/lib/zookeeper #optional in case ofpermission problem
   echo 1 > /var/lib/zookeeper/myid
   ```
4. Move to other nodes
   ```
   scp -r zookeeper-3.4.12/ ZOOKEEPER_NODE2_PRIVATE_IP:/home/ubuntu
   ```
5. Test if every nodes works, start zookeeper on each node
   ```
   ./bin/zkServer.sh start-foreground
   ```
   Open a new terminal and check status of one node
   ```
   ./bin/zkServer.sh status
   ```

### [Kafka](https://www.cnblogs.com/wxisme/p/5196302.html)
1. Download Kafka
   ```
   wget https://archive.apache.org/dist/kafka/0.8.2.2/kafka_2.11-0.8.2.2.tgz
   tar -zxvf kafka_2.11-0.8.2.2.tgz 
   ```
2. Navigate to the Apache Kafka® properties file (/config/server.properties) and customize the following:
    ```
    broker.id=0 #start from zero, each node should be different
    host.name=ZOOKEEPER_NODE1_PRIVATE_IP
    ...
    num.network.threads=3
    default.replication.factor = 2
    auto.create.topics.enable = true
    ...
    log.dirs=/var/lib/kafka/logs
    zookeeper.connect=ZOOKEEPER_NODE1_PRIVATE_IP:2181,ZOOKEEPER_NODE2_PRIVATE_IP:2181,ZOOKEEPER_NODE3_PRIVATE_IP:2181
    ```
3. Make directories for log file and give permission for writing
   ```
   sudo mkdir /var/lib/kafka/logs
   sudo chmod 0777 /var/lib/kafka/logs #optional in case of permission problem
   ```
4. Copy kafka folder to other nodes, and revise unique hostname and broker id in property file
5. First start zookeeper, then start kafka
   ```
   ./bin/kafka-server-start.sh config/server.properties
   ```
6. Test messages
   Create topic
   ```
   ./bin/kafktopics.sh -zookeeper ZOOKEEPER_NODE1_PRIVATE_IP:2181,ZOOKEEPER_NODE2_PRIVATE_IP:2181,ZOOKEEPER_NODE3_PRIVATE_IP:2181 -topic test -replication-factor 2 -partitions 3 -create
   ```
   Check topic lists
   ```
   ./bin/kafktopics.sh -zookeeper ZOOKEEPER_NODE1_PRIVATE_IP:2181,ZOOKEEPER_NODE2_PRIVATE_IP:2181,ZOOKEEPER_NODE3_PRIVATE_IP:2181 -list
   ```
   Set up producer, here we have same broker nodes as zookeeper nodes
   ```
   ./bin/kafka-console-producer.sh -broker-list ZOOKEEPER_NODE1_PRIVATE_IP:9092,ZOOKEEPER_NODE2_PRIVATE_IP:9092,ZOOKEEPER_NODE3_PRIVATE_IP:9092 -topic test
   ```
   Set up consumer on another node
   ```
   ./bin/kafka-console-consumer.sh -zookeeper ZOOKEEPER_NODE1_PRIVATE_IP:2181,ZOOKEEPER_NODE2_PRIVATE_IP:2181,ZOOKEEPER_NODE3_PRIVATE_IP:2181 -from-beginning -topic test
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


