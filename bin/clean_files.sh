#!/bin/bash
#1: must be "clean" so that we can prevent mistakenly deleting files

if [ $1 = "clean" ]; then
    source stop_script.sh
    rm -rf db/*
    source start_script.sh

    rm -rf profiles/Reservation*
    rm -rf profiles/cloud_machine_request_logs/*
    rm -rf synth_comm_array_files/*
    rm -rf image_bundle/image_bundle_logs/*
    mongo mlwebapp --eval "db.dropDatabase()"
    source stop_script.sh
    rm -rf server_logs/*
fi
