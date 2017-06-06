#!bash/bin
#1: Master Public IP
#2: Path to Hostsfile
#3: Path to .pem file

for ip in $(echo `cat $2` $1); do
    cat ~/.ssh/id_rsa.pub | ssh -q -o stricthostkeychecking=no -i $3 ubuntu@$ip 'cat >> /home/ubuntu/.ssh/authorized_keys'
done
