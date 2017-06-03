#!/bin/bash

source scripts_to_run_locally/delete_pyc_files.sh
python scripts_to_run_locally/terminate_and_show_reservations.py terminate all
python flask_endpoint_scripts/profile.py
