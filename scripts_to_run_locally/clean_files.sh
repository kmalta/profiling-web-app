#!/bin/bash
#1: must be "clean" so that we can prevent mistakenly deleting files

if [ $1 = "clean" ]; then
    rm -rf profiles/Reservation*
    rm -rf profiles/cloud_machine_request_logs/*
    rm -rf synth_comm_array_files/*
    rm -rf image_bundle/image_bundle_logs/*
    rm -rf server_logs/*
    mongo mlwebapp --eval "db.dropDatabase()"
fi

source scripts_to_run_locally/delete_pyc_files.sh
python scripts_to_run_locally/terminate_and_show_reservations.py terminate all
