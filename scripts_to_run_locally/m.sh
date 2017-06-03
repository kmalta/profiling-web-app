#!/bin/bash
#1: cloud name

LASTDIR=$(ls -t ~/profiling-web-app/profiles | head -1)
ip=$(cat ~/profiling-web-app/profiles/$LASTDIR/host_master)
ssh -i ~/profiling-web-app/cloud_configs/$1/$1-key.pem ubuntu@$ip
