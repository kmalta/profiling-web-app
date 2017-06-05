#!/bin/bash

source delete_pyc_files.sh
python terminate_and_show_reservations.py terminate all

python flask_endpoint_scripts/python_endpoint.py >> server_logs/flask_endpoint.log 2>&1 &
nf start >> server_logs/node_web_app.log 2>&1 &
