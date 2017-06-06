import sys, os, subprocess
sys.path.insert(0,'.')

import boto, errno, time
from boto.ec2.regioninfo import RegionInfo
from time import sleep, gmtime, strftime, time

from py_command_line_wrappers import *

def time_str():
    return strftime("-%Y-%m-%d-%H-%M-%S", gmtime())


def update_known_hosts(ips):
    for ip in ips:
        FNULL = open(os.devnull, 'w')
        retcode = subprocess.call(['ssh-keygen', '-q', '-R', ip], stdout=FNULL, stderr=subprocess.STDOUT)


def get_ip(instance):
    return str(instance.ip_address)

def get_priv_ip(instance):
    return str(instance.private_ip_address)

def launch_on_demand_instances(conn, instance_type, num_insts, image_id):
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
    if terminate_instances == True:
        conn.terminate_instances(instance_ids)


def start_ec2_boto_connection():
    print "Starting Boto EC2 Connection."
    region = RegionInfo(name=aws_region, endpoint=aws_endpoint)
    ec2conn = boto.connect_ec2(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key, 
        region=region)
    return ec2conn



def start_s3_boto_connection():
    print "Starting Boto S3 Connection."
    s3conn = boto.connect_s3(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key)
    return s3conn



def get_euca_worker_type(worker_type):
    worker_type = euca_instance_types[aws_instance_types.index(worker_type)]
    return worker_type

def launch_instances(conn, bid, instance_type, num_insts):
    if launch_type == 'spot':
        return spot_launch(conn, bid, instance_type, num_insts, node_image)
    elif launch_type == 'on-demand':
        return launch_and_wait(conn, instance_type, num_insts, node_image), aws_on_demand_prices[aws_instance_types.index(instance_type)]
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE LAUNCH TYPE"


def wait_ssh(ips, reservation):
    for ip in ips:
        print 'Waiting on node', ip + '.'
        flag = 0
        while(flag == 0):
            proc = py_ssh('-o connecttimeout=3 -o UserKnownHostsFile=/dev/null', ip,'true 2>/dev/null')
            if proc.returncode == 0:
                flag = 1
    return

def launch_and_wait(conn, instance_type, num_insts, image_id):
    reservation = launch_on_demand_instances(conn, instance_type, num_insts, image_id)
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
    wait_ssh(ips, reservation)
    return reservation



def spot_launch(conn, bid, instance_type, num_insts, image_id):
    print repr(bid), repr(instance_type), repr(num_insts)
    reservation = conn.request_spot_instances(float(bid), image_id, count=num_insts, type='one-time', 
                                              instance_type=instance_type, key_name=key_name, 
                                              security_groups=[security_group])
    print 'Secured reservation: ', repr(reservation)
    instances = get_instances_from_reservation(reservation)
    print 'Waiting for instances to run.'
    print repr(instances)
    for instance in instances:
        print repr(instance.ip_address)
        while instance.update() != "running":
            sleep(3)
    print 'All nodes are running.'

    ips = [instance.ip_address for instance in instances]
    print 'Updating known hosts files.'
    update_known_hosts(ips)
    print 'Waiting on SSH for each instance.'
    wait_ssh(ips, reservation)
    return reservation



def main():
    1


if __name__ == "__main__":
    main()