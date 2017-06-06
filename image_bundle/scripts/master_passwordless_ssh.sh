#!/bin/bash
#1: Path to .pem File
#2: Master Public IP

host_path=~/aws/slave_pub_ips
pem_path=~/$1

source scripts/create_ssh_keygen.sh
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

for ip in `cat $host_path`; do
    cat ~/.ssh/id_rsa.pub | ssh -q -o stricthostkeychecking=no -i $pem_path ubuntu@$ip 'cat >> ~/.ssh/authorized_keys'
done

for ip in $(echo `cat $host_path`); do
    ssh -t -t -q -o stricthostkeychecking=no ubuntu@$ip 'source scripts/create_ssh_keygen.sh;source scripts/set_local_host.sh ' $2 $host_path $pem_path
done
