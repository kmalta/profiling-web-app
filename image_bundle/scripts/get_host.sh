#!/bin/bash
#1: cloud abbrev

ip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1`

address=$1'-'${ip//./-}

echo -e $address"\n"$ip > /home/ubuntu/host
