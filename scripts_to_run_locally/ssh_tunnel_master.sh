#!/bin/bash

LASTDIR=$(ls -t ~/profiling-web-app/profiles | head -1)
ip=$(cat ~/profiling-web-app/profiles/$LASTDIR/host_master)
host=$(cat ~/profiling-web-app/profiles/$LASTDIR/masters)

declare -a ports=('4040' '8080')
port_str=''
for port in "${ports[@]}"; do
    for i in $(seq "$port" "$(($port + 10))"); do
        port_str="$port_str -L :$i:$host:$i"
    done
done

echo $port_str
ssh $port_str -i cloud_configs/aristotle/aristotle-key.pem ubuntu@$ip
