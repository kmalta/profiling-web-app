import sys
sys.path.insert(0,'.')

import boto, errno, time
from boto.ec2.regioninfo import RegionInfo
from boto.s3.key import Key
from time import sleep, gmtime, strftime, time

from py_command_line_wrappers import *

def time_str():
    return strftime("-%Y-%m-%d-%H-%M-%S", gmtime())


def update_known_hosts(ips):
    for ip in ips:
        os.system('ssh-keygen -q -R ' + ip + ' >/dev/null')



def launch_instances(conn, instance_type, num_insts, image_id):
    print 'Launching', str(num_insts), instance_type, 'instances.'
    reservation = conn.run_instances(
        image_id=image_id,
        min_count=num_insts,
        max_count=num_insts,
        key_name=key_name,
        instance_type=instance_type,
        security_groups=[security_group])
    return reservation


def get_reservations(conn):
    reservations = conn.get_all_reservations()
    return reservations

def get_instances_from_reservation(reservation):
    instances = reservation.instances
    return instances

def get_ips_from_instances(instances):
    return [instance.ip_address for instance in instances]

def reboot_instances(conn, instance_ids):
    conn.reboot_instances(instance_ids)


def terminate_instances_from_reservation(conn, reservation):
    print "Terminating Instances for Reservation: " + reservation.id + ". Arnold is Tearing it Up."
    instance_ids = [instance.id for instance in reservation.instances]
    conn.terminate_instances(instance_ids)



def aws_ec2_boto_connection():
    print "Starting Boto Connection."
    ec2conn = boto.connect_ec2(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key, 
        is_secure=False,
        port=8773)
    return ec2conn

def euca_ec2_boto_connection():
    print "Starting Boto Connection."
    ec2conn = boto.connect_euca(
        host=ec2_host,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key, 
        is_secure=False,
        port=8773, 
        path=ec2_service_path)
    return ec2conn


def start_ec2_boto_connection():
    if cloud_name == 'aristotle':
        return euca_ec2_boto_connection()
    elif cloud_name == 'aws':
        return aws_ec2_boto_connection()
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"


def s3_boto_connection():
    s3conn = boto.connect_s3(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
        is_secure=False,
        port=8773,
        path=s3_service_path,
        host=s3_host)
    return s3conn

def walrus_boto_connection():
    s3conn = boto.connect_walrus(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
        is_secure=False,
        port=8773,
        path=s3_service_path,
        host=s3_host)
    return s3conn


def start_s3_boto_connection():
    if cloud_name == 'aristotle':
        return walrus_boto_connection()
    elif cloud_name == 'aws':
        return s3_boto_connection()
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"


def get_euca_worker_type(worker_type):
    euca_instance_types = ['cg1.4xlarge', 'm1.large', 'm2.4xlarge']
    aws_instance_types = ['c4.xlarge', 'm4.xlarge', 'r4.2xlarge']
    worker_type = euca_instance_types[aws_instance_types.index(worker_type)]
    return worker_type

def spot_launch(conn, bid, instance_type, num_insts):
    if cloud_name == 'aristotle':
        return euca_spot_launch_mimicry(conn, bid, instance_type, num_insts)
    elif cloud_name == 'aws':
        return aws_spot_launch(conn, bid, instance_type, num_insts)
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"



def euca_wait_on_node(ip, max_time):
    print 'Waiting on node', ip + '.'
    times = 0
    while(times < max_time):
        proc = py_ssh('-o connecttimeout=3 -o UserKnownHostsFile=/dev/null', ip,'true 2>/dev/null')
        if proc.returncode == 0:
            return 1
        times += 1
    return 0

def euca_wait_ssh(ips, reservation):
    ips_to_redo = []
    for ip in ips:
        euca_wait_on_node(ip, 20)
    for ip in ips:
        ret_val = euca_wait_on_node(ip, 1)
        if ret_val == 0:
            ips_to_redo.append(ip)

    return ips_to_redo

def euca_wait_ssh_wrapper(conn, instance_type, num_insts, image_id):
    instance_type = get_euca_worker_type(instance_type)
    while (1):
        reservation = launch_instances(conn, instance_type, num_insts, image_id)
        print 'Secured reservation: ', repr(reservation)
        instances = get_instances_from_reservation(reservation)
        print 'Waiting for instances to run.'
        for instance in instances:
            while instance.update() != "running":
                sleep(3)
        print 'All nodes are running.'

        ips = [instance.ip_address for instance in instances]
        print 'Updating known hosts files.'
        update_known_hosts(ips)
        print 'Waiting on SSH for each instance.'
        redo_ips = euca_wait_ssh(ips, reservation)
        if redo_ips == []:
            break
        else:
            terminate_instances_from_reservation(conn, reservation)
    return reservation


def aws_wait_ssh(conn, instance_type, num_insts):
    1

def launch_and_wait(conn, instance_type, num_insts, image_id):
    if cloud_name == 'aristotle':
        return euca_wait_ssh_wrapper(conn, instance_type, num_insts, image_id)
    elif cloud_name == 'aws':
        return aws_wait_ssh(conn, instance_type, num_insts, image_id)
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"



def euca_spot_launch_mimicry(conn, bid, instance_type, num_insts):
    reservation = launch_and_wait(conn, instance_type, num_insts, node_image)
    return reservation, bid


def aws_spot_launch(conn, bid, instance_type, num_insts):
    1



def main():
    ec2_conn = start_ec2_boto_connection()
    s3_conn = start_s3_boto_connection()
    reservations = get_reservations(ec2_conn)
    print reservations
    for reservation in reservations:
        instances = get_instances_from_reservation(reservation)
        print instances


if __name__ == "__main__":
    main()