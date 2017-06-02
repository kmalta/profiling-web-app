#!bin/bash

. ~/.profile

sudo mv ~/all_hosts_file /etc/hosts
sudo chown root:root /etc/hosts
sudo chmod 644 /etc/hosts

sudo cp ~/hadoop_conf_files/hadoop-env.sh $HADOOP_CONF_DIR/hadoop-env.sh
sudo cp ~/hadoop_conf_files/core-site.xml $HADOOP_CONF_DIR/core-site.xml
sudo cp ~/hadoop_conf_files/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml
sudo cp ~/hadoop_conf_files/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
sudo cp ~/hadoop_conf_files/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
