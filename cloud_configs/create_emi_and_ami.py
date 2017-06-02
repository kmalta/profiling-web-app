import sys
sys.path.insert(0,'.')

from flask_endpoint_scripts.boto_launch_scripts import *

# def get_bucket(conn):
#     return conn.create_bucket(key_id + '-' + bucket_name)



def setup_instance(ip):
    py_cmd_line(' '.join(['cp', local_pem_path, 'image_bundle/' + '/'.join(local_pem_path.split('/')[-2:])]))
    cmd = ['tar', '-czf','image_bundle/scripts.tar.gz', '-C', 'image_bundle', 'scripts', 'ssh_config', pem_path, 'hadoop_conf_files']

    py_cmd_line(' '.join(cmd))

    py_scp_to_remote('', ip, 'image_bundle/scripts.tar.gz', '~/scripts.tar.gz')
    py_scp_to_remote('', ip, 'image_bundle/build_dependencies.sh', '~/build_dependencies.sh')
    py_ssh('', ip, 'source build_dependencies.sh')


def create_image(conn):
    reservation = launch_and_wait(conn, base_instance_type, 1, base_image)
    instance = get_instances_from_reservation(reservation)[0]
    instance_ip = instance.ip_address
    instance_id = instance.id
    setup_instance(instance_ip)
    node_image = conn.create_image(instance_id, 'pwa-node-image')
    print repr(node_image)

    #AFTER YOU WRITE SETUP
    # f = open('cloud_configs/' + cloud_name + '/' + cloud_name + '_node_image.py', 'w')
    # f.write("node_image = '" + node_image + "'")
    # f.close()





def main():
    conn = start_ec2_boto_connection()
    create_image(conn)



if __name__ == "__main__":
    main()
