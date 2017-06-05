#!/bin/bash
#1: ip
#2: remote file path
#3: local path
#4: cloud name

scp -i cloud_configs/$4/$4-key.pem ubuntu@$1:~/$2 $3