#!/bin/bash
#1: ip
#2: remote file path
#3: cloud name

scp -i cloud_configs/$3/$3-key.pem ubuntu@$1:~/$2 temp_files/