#!/bin/bash
#1: must be "clean" so that we can prevent mistakenly deleting files

nf start >> server_logs/node_web_app.log 2>&1 &

if [ $1 = "clean" ]; then
    source stop_script.sh
    source start_script.sh
    rm -rf profiles/Reservation*
    rm -rf profiles/cloud_machine_request_logs/*
    rm -rf synth_comm_array_files/*
    rm -rf image_bundle/image_bundle_logs/*
    mongo mlwebapp --eval "db.dropDatabase()"
    source stop_script.sh
    rm -rf server_logs/*
fi

source delete_pyc_files.sh
python terminate_and_show_reservations.py terminate all
