#!/bin/bash

LASTDIR=$(ls -t $PROFILE_WEB_APP_HOME/profiles | head -1)
ip=$(cat $PROFILE_WEB_APP_HOME/profiles/$LASTDIR/host_master)

declare -a ports=('4040' '8080')
port_str=''
for port in "${ports[@]}"; do
    for i in $(seq "$port" "$(($port + 10))"); do
        port_str="$port_str -L :$i:master:$i"
    done
done

echo $port_str
ssh $port_str -i $PROFILE_WEB_APP_HOME/cloud_configs/aws/aws-key.pem ubuntu@$ip
