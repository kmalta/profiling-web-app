#!/bin/bash
#1: ip
#2: remote file path
#3: local path

. ~/.bash_profiles
scp -i $PROFILE_WEB_APP_HOME/cloud_configs/aws/aws-key.pem ubuntu@$1:~/$2 $3
