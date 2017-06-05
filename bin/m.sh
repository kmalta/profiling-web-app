#!/bin/bash
#1: cloud name

LASTDIR=$(ls -t profiles | head -1)
ip=$(cat profiles/$LASTDIR/host_master)
ssh -i cloud_configs/$1/$1-key.pem ubuntu@$ip
