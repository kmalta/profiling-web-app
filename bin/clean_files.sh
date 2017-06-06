#!/bin/bash
#1: must be "clean" so that we can prevent mistakenly deleting files

. ~/.bash_profile

if [ $1 = "clean" ]; then
    source stop_script.sh > /dev/null 2>&1
    rm -rf $PROFILE_WEB_APP_HOME/db/*
    source start_script.sh > /dev/null 2>&1

    rm -rf $PROFILE_WEB_APP_HOME/profiles/Reservation*
    rm -rf $PROFILE_WEB_APP_HOME/profiles/cloud_machine_request_logs/*
    rm -rf $PROFILE_WEB_APP_HOME/synth_comm_array_files/*
    rm -rf $PROFILE_WEB_APP_HOME/image_bundle/image_bundle_logs/*
    mongo mlwebapp --eval "db.dropDatabase()" > /dev/null 2>&1
    source stop_script.sh > /dev/null 2>&1
    rm -rf $PROFILE_WEB_APP_HOME/server_logs/*
    echo
    echo "All your directories have been thoroughly cleaned."
fi
