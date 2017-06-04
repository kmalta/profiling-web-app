import sys
sys.path.insert(0,'.')

from flask_endpoint_scripts.boto_launch_scripts import *



def setup_instance(ip):
    #py_cmd_line(' '.join(['cp', local_pem_path, 'image_bundle/' + '/'.join(local_pem_path.split('/')[-2:])]))
    cmd = ['tar', '-czf','image_bundle/scripts.tar.gz', '-C', 'image_bundle', 
           'scripts', 'ssh_config', 'hadoop_conf_files','-C', '../cloud_configs', 
           '/'.join(local_pem_path.split('/')[-2:])]

    print ' '.join(cmd)
    py_cmd_line(' '.join(cmd))

    py_scp_to_remote('', ip, 'image_bundle/scripts.tar.gz', '~/scripts.tar.gz')
    py_scp_to_remote('', ip, 'image_bundle/build_dependencies.sh', '~/build_dependencies.sh')
    py_ssh('', ip, 'source build_dependencies.sh')
    #py_ssh_to_log('', ip, 'source build_dependencies.sh', 'image_bundle/image_bundle_logs/image-bundle-stdout' + time_str() + '.log', True)


def create_image(conn):
    #reservation = launch_and_wait(conn, base_instance_type, 1, base_image)

    reservation_id = 'r-0bf623c1f08c3b64f'
    reservations = get_reservations(conn)
    reservation = reservations[[str(res.id) for res in reservations].index(reservation_id)]

    instance = get_instances_from_reservation(reservation)[0]
    instance_ip = instance.ip_address
    instance_id = instance.id
    print instance_ip, instance_id

    setup_instance(instance_ip)

    node_image = instance.create_image('pwa-node-image')

    #node_image = instance.create_snapshot('pwa-node-image')

    #conn.bundle_instance()
    # print dir(instance)
    # print repr(instance.block_device_mapping)

    print repr(node_image)

    #AFTER YOU WRITE SETUP
    # f = open('cloud_configs/' + cloud_name + '/' + cloud_name + '_node_image.py', 'w')
    # f.write("node_image = '" + node_image + "'")
    # f.close()





def main():
    #conn = start_ec2_boto_connection()
    # images = conn.get_all_images()
    # snapshots = conn.get_all_snapshots()
    # print repr(images)
    # print repr(snapshots)
    #create_image(conn)
    setup_instance('54.219.185.104')



if __name__ == "__main__":
    main()
