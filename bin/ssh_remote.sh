#!/bin/bash
#1: ip

. ~/.bash_profile
ssh -o connecttimeout=60 -o stricthostkeychecking=no -i $PROFILE_WEB_APP_HOME/cloud_configs/aws/aws-key.pem ubuntu@$1
