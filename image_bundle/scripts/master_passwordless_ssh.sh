#!/bin/bash
#1: path_name
#2: master_ip
#3: master_priv_ip
#4: cloud abbrev

host_path=~/hostfile
pem_path=~/$1

source scripts/create_ssh_keygen.sh
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

sudo chown root:root /
sudo ufw disable >/dev/null
sudo ufw allow 4000:9000/tcp >/dev/null
sudo ufw allow 50000:54311/tcp >/dev/null
sudo chown ubuntu:ubuntu /

for ip in `cat $host_path`; do
    cat ~/.ssh/id_rsa.pub | ssh -q -o stricthostkeychecking=no -i $pem_path ubuntu@$ip 'cat >> ~/.ssh/authorized_keys'
done


for ip in $(echo `cat $host_path`); do
    ssh -t -t -q -o stricthostkeychecking=no ubuntu@$ip 'source scripts/create_ssh_keygen.sh;source scripts/set_local_host.sh ' $2 $host_path $pem_path $4
done
