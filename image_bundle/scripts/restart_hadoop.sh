#!/bin/bash
#1: pem path

host_path=~/hostfile
pem_path=~/$1

source /home/ubuntu/scripts/stop_hadoop.sh
sudo rm -rf /tmp/*; sudo rm -rf /mnt/namenode/*; sudo rm -rf /mnt/datanode/*; sudo rm -rf /mnt/spark/*

for ip in `cat $host_path`; do
    ssh -q -o stricthostkeychecking=no -i $pem_path ubuntu@$ip 'sudo rm -rf /tmp/*; sudo rm -rf /mnt/datanode/*; sudo rm -rf /mnt/spark/*'
done

sudo chown -R ubuntu:ubuntu /mnt

source /home/ubuntu/scripts/start_hadoop.sh
