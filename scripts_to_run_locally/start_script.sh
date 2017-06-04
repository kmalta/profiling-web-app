#!/bin/bash

source scripts_to_run_locally/delete_pyc_files.sh
python scripts_to_run_locally/terminate_and_show_reservations.py terminate all

rm -rf server_logs/*

python flask_endpoint_scripts/python_endpoint.py >> server_logs/flask_endpoint.log 2>&1 &
nf start >> server_logs/node_web_app.log 2>&1 &
