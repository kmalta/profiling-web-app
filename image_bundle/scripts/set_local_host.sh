#!bash/bin
#1: master ip
#2: path to host
#3: path to pem
#4: cloud abbrev

ip=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1`

address=$4'-'${ip//./-}

sudo chown root:root /
sudo ufw disable >/dev/null
sudo ufw allow 4000:9000/tcp >/dev/null
sudo ufw allow 50000:54311/tcp >/dev/null
sudo chown ubuntu:ubuntu /


for ip in $(echo `cat $2` $1); do
    cat ~/.ssh/id_rsa.pub | ssh -q -o stricthostkeychecking=no -i $3 ubuntu@$ip 'cat >> /home/ubuntu/.ssh/authorized_keys'
done
