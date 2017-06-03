import sys, os
sys.path.insert(0,'.')

from flask_endpoint_scripts.boto_launch_scripts import *

conn = start_ec2_boto_connection()
reservations = get_reservations(conn)


clp = sys.argv

if clp[1] == 'show':
    for i, reservation in enumerate(reservations):
        print str(i + 1) + '.', reservation.id

if clp[1] == 'terminate':
    if clp[2] == 'all':
        for reservation in reservations:
            terminate_instances_from_reservation(conn, reservation)
    else:
        indices_to_term = [int(item) - 1 for item in clp[2:]]
        for i in indices_to_term:
            terminate_instances_from_reservation(conn, reservations[i])
