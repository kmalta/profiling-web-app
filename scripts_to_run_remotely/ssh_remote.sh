#!/bin/bash
#1: ip
#2: cloud name

ssh -o connecttimeout=60 -o stricthostkeychecking=no -i ~/profiling-web-app/cloud_configs/$2/$2-key.pem ubuntu@$1