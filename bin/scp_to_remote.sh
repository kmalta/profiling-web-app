#!/bin/bash
#1: ip
#2: local file path
#3: remote file path

. ~/.bash_profile
scp -i $PROFILE_WEB_APP_HOME/cloud_configs/aws/aws-key.pem temp_files/$2 ubuntu@$1:~/$3