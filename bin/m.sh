#!/bin/bash

. ~/.bash_profile
LASTDIR=$(ls -t $PROFILE_WEB_APP_HOME/profiles | head -1)
ip=$(cat $PROFILE_WEB_APP_HOME/profiles/$LASTDIR/master_ip)
ssh -i $PROFILE_WEB_APP_HOME/cloud_configs/aws/aws-key.pem ubuntu@$ip
