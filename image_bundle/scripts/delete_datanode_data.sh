#!/bin/bash

for ip in `cat ~/hostfile`; do
    ssh ubuntu@$ip 'sudo rm -rf /tmp/*; sudo rm -rf /mnt/datanode/*'
done
