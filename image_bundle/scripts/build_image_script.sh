#!/bin/bash

sudo rm -f ~/.bash_history
sudo rm -f /etc/udev/rules.d/70*-net.rules
sudo rm -rf /root/linux-rootfs-resize*
sudo rm -rf /root/euca2ools*
sudo rm -rf /var/lib/cloud/instance /var/lib/cloud/instances/i*
sudo rm ~/.ssh/*
sudo echo -e ' ' > ~/.ssh/authorized_keys

rm /home/ubuntu/build-dependencies.sh

# Specific to ubuntu
sudo apt-get -y upgrade
sudo apt-get -y dist-upgrade
sudo apt-get -y autoremove

# sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1; sudo sysctl -w net.ipv6.conf.default.disable_ipv6=1

# sudo iptables -P INPUT ACCEPT
# sudo iptables -P OUTPUT ACCEPT
# sudo iptables -P FORWARD ACCEPT
# sudo iptables -F
