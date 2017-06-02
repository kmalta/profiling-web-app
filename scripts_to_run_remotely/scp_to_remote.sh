#!/bin/bash
#1: ip
#2: local file path
#3: remote file path
#4: cloud name

scp -i cloud_configs/$4/$4-key.pem temp_files/$2 ubuntu@$1:~/$3