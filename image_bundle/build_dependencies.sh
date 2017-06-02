#!/bin/bash

tar -xzf scripts.tar.gz

sudo apt-get update
sudo apt-get -y install g++ make autoconf git libtool uuid-dev openssh-server cmake bc libopenmpi-dev openmpi-bin libssl-dev libnuma-dev 
sudo apt-get -y install python-dev python-numpy python-pip python-scipy python-yaml protobuf-compiler subversion libxml2-dev libxslt-dev 
sudo apt-get -y install ssh rsync zlibc zlib1g zlib1g-dev libbz2-1.0 libbz2-dev openjdk-7-jdk


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
wget http://apache.mirrors.ionfish.org/spark/spark-2.0.0/spark-2.0.0-bin-hadoop2.7.tgz
tar -xvvf spark-2.0.0-bin-hadoop2.7.tgz
mv spark-2.0.0-bin-hadoop2.7 spark-2.0.0

echo "export PATH='~/spark-2.0.0/bin/:$PATH'" >> ~/.bashrc
. ~/.bashrc


sudo mv ~/hadoop-2.7.3 /usr/local/hadoop
echo -e "export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64" >> ~/.profile
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
mkdir /mnt/spark


sudo mv ~/ssh_config /etc/ssh/ssh_config
sudo chown root:root /etc/ssh/ssh_config
sudo chmod 644 /etc/ssh/ssh_config


sudo pip install setuptools
sudo pip install boto
rm -rf *gz

cd ~
mv scripts_to_run_remotely scripts
source ~/scripts/build_image_script.sh
