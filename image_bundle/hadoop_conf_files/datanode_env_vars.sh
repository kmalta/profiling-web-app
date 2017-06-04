#!bin/bash
#1: master priv ip
#2: master host
#3: cloud abbrev

ip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1`

address=$3'-'${ip//./-}

. ~/.profile
sudo mkdir /mnt/datanode
sudo chown -R ubuntu $HADOOP_HOME
sudo chown -R ubuntu /mnt/datanode

cp $SPARK_HOME_DIR/conf/spark-env.sh.template $SPARK_HOME_DIR/conf/spark-env.sh
echo -e "export SPARK_MASTER_HOST="$2 >> $SPARK_HOME_DIR/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_IP='$ip >> $SPARK_HOME_DIR/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_HOST='$address >> $SPARK_HOME_DIR/conf/spark-env.sh
echo -e 'export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop' >> $SPARK_HOME_DIR/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_DIRS=/mnt/spark' >> $SPARK_HOME_DIR/conf/spark-env.sh