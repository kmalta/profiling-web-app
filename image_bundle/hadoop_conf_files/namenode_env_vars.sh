#!bin/bash
#1: cloud abbrev

ip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1`

address=$1'-'${ip//./-}

. ~/.profile
sudo mkdir /mnt/namenode
sudo mv ~/masters $HADOOP_CONF_DIR/masters
sudo mv ~/slaves $HADOOP_CONF_DIR/slaves
sudo chown -R ubuntu $HADOOP_HOME
sudo chown -R ubuntu /mnt/namenode


cp ~/spark-2.0.0/conf/spark-env.sh.template ~/spark-2.0.0/conf/spark-env.sh
echo -e "export SPARK_MASTER_HOST="$address >> ~/spark-2.0.0/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_IP='$ip >> ~/spark-2.0.0/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_HOST='$address >> ~/spark-2.0.0/conf/spark-env.sh
echo -e 'export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop' >> ~/spark-2.0.0/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_DIRS=/mnt/spark' >> ~/spark-2.0.0/conf/spark-env.sh
