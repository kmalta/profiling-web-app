import boto, errno, time
from boto.ec2.regioninfo import RegionInfo
from boto.s3.key import Key
from time import sleep, gmtime, strftime

from py_command_line_wrappers import *


def time_str():
    return strftime("-%Y-%m-%d-%H-%M-%S", gmtime())


def update_known_hosts(ips):
    for ip in ips:
        os.system('ssh-keygen -q -R ' + ip)

def wait_on_node(ip, max_time):
    print 'Waiting on node', ip + '.'
    times = 0
    while(times < max_time):
        proc = py_ssh('-o connecttimeout=3 -o UserKnownHostsFile=/dev/null', ip,'true 2>/dev/null')
        if proc.returncode == 0:
            return 1
        times += 1
    return 0

def wait_ssh(ips, reservation):
    ips_to_redo = []
    for ip in ips:
        wait_on_node(ip, 10)
    for ip in ips:
        ret_val = wait_on_node(ip, 1)
        if ret_val == 0:
            ips_to_redo.append(ip)

    return ips_to_redo


def launch_instances(conn, instance_type, num_insts):
    print 'Launching', str(num_insts), instance_type, 'instances.'
    reservation = conn.run_instances(
        image_id=node_image,
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
    print "Terminating Instances. Arnold is tearing it up."
    instance_ids = [instance.id for instance in reservation.instances]
    conn.terminate_instances(instance_ids)


def start_ec2_boto_connection():
    print "Starting Boto Connection."
    region = RegionInfo(name=cloud_name, endpoint=ec2_host)
    ec2conn = boto.connect_ec2(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key, 
        is_secure=False,
        port=8773, 
        path=ec2_service_path, 
        region=region)
    return ec2conn

def start_s3_boto_connection():
    s3conn = boto.connect_s3(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
        is_secure=False,
        port=8773,
        path=s3_service_path,
        host=s3_host)
    return s3conn



def aws_spot_launch(conn, bid, instance_type, num_insts):
    1

def euca_spot_launch_mimicry(conn, bid, instance_type, num_insts):
    euca_instance_types = ['cg1.4xlarge', 'm1.large', 'm2.4xlarge']
    aws_instance_types = ['c4.xlarge', 'm4.xlarge', 'r4.2xlarge']
    instance_type = euca_instance_types[aws_instance_types.index(instance_type)]
    while (1):
        reservation = launch_instances(conn, instance_type, num_insts)
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
        redo_ips = wait_ssh(ips, reservation)
        if redo_ips == []:
            return reservation, bid
        else:
            terminate_instances_from_reservation(conn, reservation)




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