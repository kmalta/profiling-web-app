#!/bin/bash

sudo su
source ~/scripts/stop_hadoop.sh
source ~/scripts/delete_datanode_data.sh
sudo rm -rf /tmp/*; sudo rm -rf /mnt/namenode/*
source ~/scripts/start_hadoop.sh
