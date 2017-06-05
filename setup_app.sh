#!/bin/bash

#THIS IS ONLY TESTED FOR OSX EL CAPITAN

#UPDATE PATH VARIABLES
echo -e 'export PROFILE_WEB_APP_HOME="$(pwd)"' >> ~/.bash_profile
echo -e 'export PATH="$PROFILE_WEB_APP_HOME/bin:${PATH}"' >> ~/.bash_profile
. ~/.bash_profile

#CREATE DIRS
mkdir data_configs db image_bundle/image_bundle_logs synth_comm_array_files server_logs
mkdir -p profiles/cloud_machine_request_logs

#CREATE CLOUD FILES
touch cloud_configs/aws/aws_node_image.py

#GET NODE AND NODE MODULES
brew update
brew install node
npm --prefix $PROFILE_WEB_APP_HOME/node_src install

#DOWNLOAD MONGODB
curl -O https://fastdl.mongodb.org/osx/mongodb-osx-x86_64-3.0.4.tgz
tar -zxvf mongodb-osx-x86_64-3.0.4.tgz
mkdir -p mongodb
mv mongodb-osx-x86_64-3.0.4/ mongodb
rm mongodb-osx-x86_64-3.0.4.tgz

#SET MONGODB PATH VARIABLES
echo -e 'export MONGODB_HOME="$PROFILE_WEB_APP_HOME/mongodb"' >> ~/.bash_profile
echo -e 'export PATH="$MONGODB_HOME/bin:${PATH}"' >> ~/.bash_profile
. ~/.bash_profile


#MAKE NODE IMAGE
python $PROFILE_WEB_APP_HOME/cloud_configs/create_ami.py
python $PROFILE_WEB_APP_HOME/bin/terminate_and_show_reservations.py
