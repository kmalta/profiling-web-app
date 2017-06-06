#!bin/bash
#1: Replication Factor for HDFS
#2: Number of Slaves

. ~/.profile

sudo mv hosts_file /etc/hosts
sudo chown root:root /etc/hosts
sudo chmod 644 /etc/hosts

sudo mkdir /mnt/namenode
sudo chown -R ubuntu $HADOOP_HOME
sudo chown -R ubuntu /mnt/namenode

cp $SPARK_HOME_DIR/conf/spark-env.sh.template $SPARK_HOME_DIR/conf/spark-env.sh
echo -e 'export SPARK_LOCAL_HOST=master'$address >> $SPARK_HOME_DIR/conf/spark-env.sh

echo -e $1"</value>
  </property>
</configuration>" >> $HADOOP_CONF_DIR/hdfs-site.xml

sudo chown ubuntu:ubuntu $HADOOP_CONF_DIR/slaves
for i in {1..$2}; do
   echo -e "Slave"$2 >> $HADOOP_CONF_DIR/slaves
done
