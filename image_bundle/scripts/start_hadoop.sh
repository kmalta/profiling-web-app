#!bin/bash
#1: num_times

. ~/.profile
echo -e "Y" | hdfs namenode -format
start-dfs.sh
