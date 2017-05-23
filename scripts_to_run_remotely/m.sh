#!/bin/bash
LASTDIR=$(ls -t ~/profiling-web-app/profiles | head -1)
ip=$(cat ~/profiling-web-app/profiles/$LASTDIR/host_master)
ssh -i ~/MLSchedule/cloud_configs/aristotle/aristotle-key.pem ubuntu@$ip
