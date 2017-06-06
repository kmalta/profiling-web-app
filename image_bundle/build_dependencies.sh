#!/bin/bash

tar -xzf scripts.tar.gz

sudo apt-get update
sudo apt-get -y install g++ make autoconf git libtool uuid-dev openssh-server cmake bc libopenmpi-dev openmpi-bin libssl-dev libnuma-dev 
sudo apt-get -y install python-dev python-numpy python-pip python-scipy python-yaml protobuf-compiler subversion libxml2-dev libxslt-dev 
sudo apt-get -y install ssh rsync zlibc zlib1g zlib1g-dev libbz2-1.0 libbz2-dev
sudo apt-get -y install openjdk-8-jdk

sudo -H pip install --upgrade pip
sudo -H pip install setuptools
sudo -H pip install boto


wget http://www.scala-lang.org/files/archive/scala-2.11.7.tgz
sudo mkdir ~/scala
sudo tar xvf scala-2.11.7.tgz -C ~/scala/

echo -e "export SCALA_HOME=~/scala-2.11.7" >> ~/.bashrc
echo -e "export PATH=$SCALA_HOME/bin:$PATH" >> ~/.bashrc
source ~/.bashrc

cd ~
wget http://apache.claz.org/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz
tar -xvvf hadoop-2.7.3.tar.gz


cd ~
wget http://apache.mirrors.ionfish.org/spark/spark-2.0.2/spark-2.0.2-bin-hadoop2.7.tgz
tar -xvvf spark-2.0.2-bin-hadoop2.7.tgz
mv spark-2.0.2-bin-hadoop2.7 spark-2.0.2

echo "export SPARK_HOME_DIR=/home/ubuntu/spark-2.0.2" >> ~/.bashrc
echo "export SPARK_HOME_DIR=/home/ubuntu/spark-2.0.2" >> ~/.profile
echo "export PATH='$SPARK_HOME_DIR/bin/:$PATH'" >> ~/.bashrc
. ~/.bashrc


sudo mv ~/hadoop-2.7.3 /usr/local/hadoop
echo -e "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.profile
echo -e "export HADOOP_HOME=/usr/local/hadoop" >> ~/.profile
echo -e "export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop" >> ~/.profile
. ~/.profile

echo -e "export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin" >> ~/.profile
echo -e "export HADOOP_MAPRED_HOME=$HADOOP_HOME" >> ~/.profile
echo -e "export HADOOP_COMMON_HOME=$HADOOP_HOME" >> ~/.profile
echo -e "export HADOOP_HDFS_HOME=$HADOOP_HOME" >> ~/.profile
echo -e "export YARN_HOME=$HADOOP_HOME" >> ~/.profile
echo -e "export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native" >> ~/.profile
echo -e "export HADOOP_OPTS=-Djava.library.path="$HADOOP_HOME"/lib/native" >> ~/.profile
. ~/.profile

sudo chown ubuntu:ubuntu /mnt
mkdir ~/jars
mv pwa-logistic-regression_2.11-1.0.jar jars

sudo mv ~/hadoop_conf_files/hadoop-env.sh $HADOOP_CONF_DIR/hadoop-env.sh
sudo mv ~/hadoop_conf_files/core-site.xml $HADOOP_CONF_DIR/core-site.xml
sudo mv ~/hadoop_conf_files/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
sudo mv ~/hadoop_conf_files/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
sudo mv ~/hadoop_conf_files/hadoop-log4j.properties $HADOOP_CONF_DIR/log4j.properties


sudo rm $HADOOP_CONF_DIR/slaves
sudo touch $HADOOP_CONF_DIR/masters $HADOOP_CONF_DIR/slaves
echo -e "Master" >> temp_file
sudo mv temp_file $HADOOP_CONF_DIR/masters

sudo mv ~/hadoop_conf_files/spark-env.sh $SPARK_HOME_DIR/conf/spark-env.sh
sudo mv ~/hadoop_conf_files/log4j.properties $SPARK_HOME_DIR/conf/log4j.properties

sudo mv spark_machine_conf_files $SPARK_HOME_DIR/conf/spark_machine_conf_files

rm -rf *gz
rm -rf ~/hadoop_conf_files

sudo chown ubuntu:ubuntu /etc/ssh/ssh_config
sudo chmod 644 /etc/ssh/ssh_config
echo -e "    StrictHostKeyChecking no" >> /etc/ssh/ssh_config
sudo chown root:root /etc/ssh/ssh_config

sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1; sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1
