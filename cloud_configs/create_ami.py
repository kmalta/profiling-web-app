import sys
sys.path.insert(0,'.')

from flask_endpoint_scripts.boto_launch_scripts import *
from boto.ec2.blockdevicemapping import BlockDeviceMapping, EBSBlockDeviceType


def setup_instance(ip):
    cmd = ['tar', '-czf','image_bundle/scripts.tar.gz', '-C', 'image_bundle', 
           'scripts', 'ssh_config', 'hadoop_conf_files','-C', '../cloud_configs', 
           '/'.join(local_pem_path.split('/')[-2:])]

    py_cmd_line(' '.join(cmd))

    py_scp_to_remote('', ip, 'image_bundle/scripts.tar.gz', '~/scripts.tar.gz')
    py_scp_to_remote('', ip, 'image_bundle/build_dependencies.sh', '~/build_dependencies.sh')

    log_file = 'image_bundle/image_bundle_logs/image-bundle-stdout' + time_str() + '.log'
    py_ssh_to_log('', ip, 'source build_dependencies.sh', log_file, True)
    py_ssh_to_log('', ip, 'rm build_dependencies.sh', log_file, True)

    return log_file


def create_image(conn):

    reservation = None
    if launch_type == 'on-demand':
        reservation = launch_and_wait(conn, base_instance_type, 1, base_image)

    instance = get_instances_from_reservation(reservation)[0]
    instance_ip = instance.ip_address
    instance_id = instance.id
    
    log_file = setup_instance(instance_ip)

    boot_disk = EBSBlockDeviceType()
    boot_disk.size = 50
    bdm = BlockDeviceMapping()
    bdm['/dev/sda1'] = boot_disk

    global node_image

    try:
        images = conn.get_all_images(owners=['self'])
        for image in images:
            image.deregister()
        f = open('cloud_configs/' + cloud_name + '/' + cloud_name + '_node_image.py', 'w')
        f.write("node_image = 'DEREGISTERED!'")
        f.close()
    except:
        1

    node_image = conn.create_image(instance_id, 'AWS-pwa-node-image', block_device_mapping = bdm)

    image = conn.get_all_images(image_ids=[node_image])[0]

    f = open(log_file, 'a+')

    while image.state == 'pending':
        sleep(15)
        f.write("Image upload state: " + image.state + '\n')
        image.update()
    f.write("Image upload state: " + image.state + '\n')

    if image.state == 'failed':
        sys.exit("AMI CREATION FAILED!")

    f.write('\n'*2)
    f.write('#'*30 + '\n')
    f.write('#'*30 + '\n\n')
    f.write("node_image = '" + str(node_image) + "'\n\n")
    f.write('#'*30 + '\n')
    f.write('#'*30 + '\n')
    f.close()

    f = open('cloud_configs/' + cloud_name + '/' + cloud_name + '_node_image.py', 'w')
    f.write("node_image = '" + str(node_image) + "'")
    f.close()



def main():
    conn = start_ec2_boto_connection()
    create_image(conn)



if __name__ == "__main__":
    main()
