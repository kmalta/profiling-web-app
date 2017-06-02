import sys, os
sys.path.insert(0,'.')

from flask_endpoint_scripts.boto_launch_scripts import *
from process_results import *
from barrier import *


def get_host(ip, working_dir):
    if os.path.isfile(working_dir + '/host'):
        os.system('rm ' + working_dir + '/host')
    py_ssh('', ip, 'source scripts/get_host.sh ' + cloud_abbrev)
    py_scp_to_local('', ip, '~/host', working_dir + '/host')

    f = open(working_dir + '/host', 'r')
    data = f.readlines()
    f.close()
    return data[0].strip(), data[1].strip()


def get_all_hosts(master_ip, ips, working_dir):
    print 'Creating Node Data Structure.'
    nodes_info = []
    master_host, master_priv_ip = get_host(master_ip, working_dir)
    nodes_info.append([master_ip, master_host, master_priv_ip])

    for ip in ips:
        host, priv_ip = get_host(ip, working_dir)
        nodes_info.append([ip, host, priv_ip])

    return nodes_info

def create_core_site_file(nodes_info, idx):
    py_ssh('', nodes_info[idx][0], 'cat hadoop_conf_files/core_site_beginning.xml host_master_tmp colon host_port_tmp hadoop_conf_files/core_site_ending.xml > hadoop_conf_files/core-site.xml')

def create_yarn_site_file(nodes_info, idx):
    port = 9000

    py_ssh('', nodes_info[idx][0], "echo -ne " + str(nodes_info[0][1]) + " > host_master_tmp; " + 
                                   "echo -ne : > colon; " + 
                                   "echo -ne " + str(port) + " > host_port_tmp")
    py_ssh('', nodes_info[idx][0], 'cat hadoop_conf_files/yarn_site_beginning.xml host_master_tmp hadoop_conf_files/yarn_site_ending.xml > hadoop_conf_files/yarn-site.xml')


def create_masters_file(nodes_info, working_dir):
    f = open(working_dir + '/masters', 'w')
    f.write(nodes_info[0][1] + '\n')
    f.close()

def create_slaves_file(nodes_info, working_dir):
    f = open(working_dir + '/slaves', 'w')
    count = 0
    for node in nodes_info[1:]:
        count += 1
        f.write(node[1] + '\n')
    f.close()

def create_etc_hosts_file(nodes_info, idx, working_dir):
    f = open(working_dir + '/hosts_file_beginning', 'w')
    f.write('127.0.0.1 localhost\n')
    f.write(nodes_info[0][2] + ' ' + nodes_info[0][1] + '\n')
    count = 0
    for node in nodes_info[1:]:
        count += 1
        f.write(node[2] + ' ' + node[1] + '\n')
    f.write('\n')
    f.close()
    os.system('cat ' + working_dir + '/hosts_file_beginning ' + working_dir + '/hosts_file_end > ' + working_dir + '/all_hosts_file')


def setup_passwordless_ssh(master_ip, master_priv_ip):
    cmd_arr = ['source ~/scripts/master_passwordless_ssh.sh', remote_pem_path, master_ip, master_priv_ip, cloud_abbrev]
    py_ssh('', master_ip, ' '.join(cmd_arr))




def configure_master_node(nodes_info, working_dir):
    master_ip = nodes_info[0][0]
    master_priv_ip = nodes_info[0][2]

    py_scp_to_remote('', master_ip, working_dir + '/masters', 'masters')
    py_scp_to_remote('', master_ip, working_dir + '/slaves', 'slaves')

    py_ssh('', master_ip, 'source hadoop_conf_files/all_env_vars.sh')
    setup_passwordless_ssh(master_ip, master_priv_ip)
    py_ssh('', master_ip, 'source hadoop_conf_files/namenode_env_vars.sh ' + cloud_abbrev)



def configure_slave_node(nodes_info, idx):
    ip = nodes_info[idx][0]
    py_ssh('', ip, 'source hadoop_conf_files/all_env_vars.sh')
    py_ssh('', ip, 'source hadoop_conf_files/datanode_env_vars.sh ' + nodes_info[0][2] + ' ' + nodes_info[0][1] + ' ' + cloud_abbrev)


def configure_spark(nodes_info, working_dir):
    f = open(working_dir + '/spark_slaves', 'w')
    for node in nodes_info[1:]:
        f.write(node[0] + '\n')
    f.close()

    py_scp_to_remote('', nodes_info[0][0], working_dir + '/spark_slaves', 'spark-2.0.0/conf/slaves')
    for node in nodes_info:
        #REMOVE ON REIMAGE
        py_ssh('', node[0], 'echo -e export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop >> ~/spark-2.0.0/conf/spark-env.sh')
        py_ssh('', node[0], 'echo -e export SPARK_LOCAL_DIRS=/mnt/spark >> ~/spark-2.0.0/conf/spark-env.sh')


def start_spark(master_ip):
    py_ssh('', master_ip, 'spark-2.0.0/sbin/start-master.sh')
    py_ssh('', master_ip, 'spark-2.0.0/sbin/start-slaves.sh')

def stop_spark(master_ip):
    py_ssh('', master_ip, 'spark-2.0.0/sbin/stop-slaves.sh')
    py_ssh('', master_ip, 'spark-2.0.0/sbin/stop-master.sh')

def scala_send_spark_job(nodes_info, jar_path):
    for node in nodes_info:
        py_scp_to_remote('', node[0], jar_path, 'jars/' + jar_path.split('/')[-1])

def euca_get_params(worker_type, num_cores, working_dir):
    worker_type = get_euca_worker_type(worker_type)
    if 'hi1.4xlarge' in worker_type:
        os.system('cp spark_conf_files/' + cloud_name + '/hi1.4xlarge.conf ' + working_dir + '/spark-defaults.conf')
        return '35000m', '35000m', '--conf spark.driver.maxResultSize=7g', 2*num_cores
    elif 'm1.large' in worker_type:
        os.system('cp spark_conf_files/' + cloud_name + '/m1.large.conf ' + working_dir + '/spark-defaults.conf')
        return '11500m', '11500m', '--conf spark.driver.maxResultSize=7g', num_cores
    else:
        os.system('cp spark_conf_files/' + cloud_name + '/cg1.4xlarge.conf ' + working_dir + '/spark-defaults.conf')
        return '4000m', '4000m', '', num_cores

def aws_get_params(worker_type, num_cores, working_dir):
    if 'r4.2xlarge' in worker_type:
        os.system('cp spark_conf_files/' + cloud_name + '/r4.2xlarge.conf ' + working_dir + '/spark-defaults.conf')
        return '48000m', '48000m', '--conf spark.driver.maxResultSize=10g', 2*num_cores
    elif 'm4.xlarge' in worker_type:
        os.system('cp spark_conf_files/' + cloud_name + '/m4.xlarge.conf ' + working_dir + '/spark-defaults.conf')
        return '11500m', '11500m', '--conf spark.driver.maxResultSize=7g', num_cores
    else:
        os.system('cp spark_conf_files/' + cloud_name + '/c4.xlarge.conf ' + working_dir + '/spark-defaults.conf')
        return '4000m', '4000m', '', num_cores



def get_params(worker_type, num_machs, working_dir):
    num_cores = num_machs*4
    if cloud_name == 'aristotle':
        return euca_get_params(worker_type, num_cores, working_dir)
    elif cloud_name == 'aws':
        return aws_get_params(worker_type, num_cores, working_dir)
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"


def get_cores(worker_type, num_machs):
    t1, t2, t3, num_cores = get_params(worker_type, num_machs, 'spark_conf_files')
    return num_cores


def clean_up_job(dataset, master_ip, nodes_info):
    py_ssh('', master_ip, '/usr/local/hadoop/bin/hdfs dfs -rm /' + dataset + '; /usr/local/hadoop/bin/hdfs dfs -ls /')

def scala_run_spark_job(nodes_info, worker_type, master_port, file_name, hadoop_master_port, jar, num_features, iterations, log_path, synth):


    #NON-YARN
    driver_mem = ''
    executor_mem = ''
    spark_max_result = ''
    num_machs = len(nodes_info[1:])
    num_cores = 4*num_machs
    num_partitions = num_cores


    for node in nodes_info:
        py_scp_to_remote('', node[0], 'spark_conf_files/log4j.properties', '~/spark-2.0.0/conf/log4j.properties')
        py_scp_to_remote('', node[0], 'spark_conf_files/hadoop-log4j.properties', '~/log4j.properties')
        py_ssh('', node[0], 'sudo mv ~/log4j.properties /usr/local/hadoop/etc/hadoop/log4j.properties')


    local_dir = '--conf spark.local.dir=/mnt/spark/'

    driver_mem, executor_mem, spark_max_reult, num_cores = get_params(worker_type, num_cores, '/'.join(log_path.split('/')[:-2]))

    for node in nodes_info:
        py_scp_to_remote('', node[0], 'spark_conf_files/spark-defaults.conf', '~/spark-2.0.0/conf/spark-defaults.conf')



    run_str = [
               '~/spark-2.0.0/bin/spark-submit',
               '--verbose',
               '--master', 'spark://' + nodes_info[0][1] + ':7077',
               '--deploy-mode client ',
               '--driver-memory ' + driver_mem,
               '--executor-memory ' + executor_mem,
               spark_max_result,
               '--num-executors', str(num_machs),\
               '--conf spark.default.parallelism=' + str(num_cores),
               local_dir,
               jar_pref + jar,
               str(num_features), nodes_info[0][1], str(hadoop_master_port),
               file_name, str(iterations), str(num_partitions)
              ]

    print log_path
    print "@@@@@@@@@@@@@@@  " + ' '.join(run_str)
    py_ssh_to_log('', nodes_info[0][0], ' '.join(run_str), log_path, False)
    start_time = time()


    time_out_check_path = log_path.split('profile_logs')[0] + 'time_out_check'
    finished_flag = 0
    if synth == False:
        finished_flag = 0
        while(time() < 600 + start_time):
            os.system('rm ' + time_out_check_path)
            py_ssh_to_log('', nodes_info[0][0], 'jps', time_out_check_path, True)
            f = open(time_out_check_path, 'r')
            output = f.read()
            f.close()
            if 'SparkSubmit' not in output and '-- process information unavailable' not in output:
                finished_flag = 1
                break
            sleep(5)
    else:
        sleep(3600)

    if finished_flag == 0:
        os.system('rm ' + time_out_check_path)
        py_ssh_to_log('', nodes_info[0][0], 'jps', time_out_check_path, True)
        f = open(time_out_check_path, 'r')
        for line in f:
            if 'SparkSubmit' in line or '-- process information unavailable' in line:
                pid = line.split()[0]
                py_ssh('', nodes_info[0][0], 'kill ' + pid)
        f.close()

    return



def create_hdfs_site_file(nodes_info, replication, tempdir_path, idx):

    py_ssh('', nodes_info[idx][0], "echo -ne " + str(replication) + " > replication_tmp; " + 
                                   "echo -ne file://" + tempdir_path + "/namenode > namenode_path; " + 
                                   "echo -ne file://" + tempdir_path + "/datanode > datanode_path")
    cat_arg = ['cat hadoop_conf_files/hdfs_site_beginning.xml replication_tmp ' + 
               'hadoop_conf_files/hdfs_site_middle_1.xml namenode_path ' + 
               'hadoop_conf_files/hdfs_site_middle_1.xml datanode_path ' + 
               'hadoop_conf_files/hdfs_site_ending.xml ' + 
               '> hadoop_conf_files/hdfs-site.xml']
    py_ssh('', nodes_info[idx][0], cat_arg[0])


def configure_hadoop(nodes_info, replication, working_dir):

    #PARAMS FOR HADOOP
    tempdir_path = '/mnt'
    num_machs = len(nodes_info) - 1

    if num_machs < replication:
        replication = num_machs


    f = open(working_dir + '/hostfile', 'w')
    for node in nodes_info[1:]:
        f.write(node[0] + '\n')
    f.close()

    preconfigure_nodes(nodes_info, working_dir)

    for i, node in enumerate(nodes_info):
        create_yarn_site_file(nodes_info, i)
        create_core_site_file(nodes_info, i)
        create_hdfs_site_file(nodes_info, replication, tempdir_path, i)

        py_scp_to_remote('', node[0], working_dir + '/hostfile', 'hostfile')
        create_etc_hosts_file(nodes_info, i, working_dir)
        py_scp_to_remote('', node[0], working_dir + '/all_hosts_file', 'all_hosts_file')





def configure_nodes(nodes_info, working_dir):

    for idx in range(len(nodes_info) - 1):
        configure_slave_node(nodes_info, idx + 1)

    configure_master_node(nodes_info, working_dir)

def preconfigure_nodes(nodes_info, working_dir):
    create_masters_file(nodes_info, working_dir)
    create_slaves_file(nodes_info, working_dir)





def get_dataset(s3url, master_ip, working_dir):

    get_data_arr = ['python scripts/get_s3_file_using_boto.py', s3url, cloud_name, key_id, secret_key, s3_service_path, s3_host]
    get_data = ' '.join(get_data_arr)

    flag = 0
    py_ssh('', master_ip, get_data)
    while(1):
        sleep(3)
        py_scp_to_local('', master_ip, 'check_if_file_written', working_dir + '/s3_file_written')
        f = open(working_dir + '/s3_file_written', 'r')
        if '1' in f.read():
            os.system('rm ' + working_dir + '/s3_file_written')
            break
        elif '2' in f.read():
            print "An error occurred while retrieving the data.  We will loop again."
            os.system('rm ' + working_dir + '/s3_file_written')
            py_ssh('', master_ip, get_data)
        if flag == 0:
            print 'Waiting in loop to get the dataset from S3.'
        flag = 1




def configure_machines_for_spark_job_experiments(s3url, profile_dir, replication, instance_ips, test):

    dataset = s3url.split('/')[-1]


    log_dir = profile_dir + '/profile_logs'

    master_ip = instance_ips[0]
    f = open(profile_dir + '/host_master', 'w')
    f.write(master_ip + '\n')
    f.close()

    ips = instance_ips[1:]
    nodes_info = get_all_hosts(master_ip, ips, profile_dir)
    if test == True:
        return dataset, nodes_info

    os.system('cp config_file_templates/hosts_file_end ' + profile_dir + '/')

    py_ssh('', master_ip, 'sudo cp ~/.ssh/authorized_keys /root/.ssh/')
    user = 'root'


    ###
    #remove all this on reimage

    for node in nodes_info:
        py_cmd_line('tar -czf image_bundle/not_just_scripts.tar.gz -C image_bundle scripts hadoop_conf_files >/dev/null')
        py_scp_to_remote('', node[0], 'image_bundle/not_just_scripts.tar.gz', '~/not_just_scripts.tar.gz')
        py_ssh('', node[0], 'rm -rf scripts; rm -rf hadoop_conf_files; mv ~/not_just_scripts.tar.gz ~/scripts.tar.gz; tar -xzf scripts.tar.gz >/dev/null')

    for ip in ips:
        1#py_ssh('', ip, 'sudo chown ubuntu:ubuntu /; sudo chown ubuntu:ubuntu /mnt; mkdir /mnt/spark')

    py_ssh('', master_ip, 'pip install boto')
    #py_ssh('', master_ip, 'sudo chown ubuntu:ubuntu /; sudo chown ubuntu:ubuntu /mnt; mkdir /mnt/spark;')






    get_dataset(s3url, master_ip, profile_dir)

    configure_hadoop(nodes_info, replication, profile_dir)
    configure_nodes(nodes_info, profile_dir)
    configure_spark(nodes_info, profile_dir)
    py_ssh('', master_ip, 'source scripts/restart_hadoop.sh')

    start_spark(master_ip)

    return dataset, nodes_info



def create_comm_hdfs_file(dataset, master_ip, comm_samples):
    py_ssh('', master_ip, 'head -n ' + str(comm_samples) + ' /mnt/' + dataset + ' > /mnt/' + dataset + '_comm; /usr/local/hadoop/bin/hdfs dfs -put /mnt/' + dataset + '_comm /; /usr/local/hadoop/bin/hdfs dfs -ls /')

def create_full_hdfs_file(dataset, master_ip):
    py_ssh('', master_ip, '/usr/local/hadoop/bin/hdfs dfs -put /mnt/' + dataset + ' /; /usr/local/hadoop/bin/hdfs dfs -ls /')

def create_synth_hdfs_file(features, master_ip, comm_samples):
    dataset = 'synth_' + str(features)
    py_scp_to_remote('', master_ip, 'synth_datasets/' + dataset, '/mnt')
    py_ssh('', master_ip, 'head -n ' + str(comm_samples) + ' /mnt/' + dataset + ' > /mnt/' + dataset + '_temp; /usr/local/hadoop/bin/hdfs dfs -put /mnt/' + dataset + '_temp /' + dataset + '; /usr/local/hadoop/bin/hdfs dfs -ls /')


def run_spark_experiment(dataset, nodes_info, worker_type, jar_path, num_features, iterations, log_path, synth, original_dataset):
    master_ip = nodes_info[0][0]
    comm_samples = get_cores(worker_type, len(nodes_info) - 1)

    scala_send_spark_job(nodes_info, jar_path)
    if 'comm' in dataset:
        create_comm_hdfs_file('_'.join(dataset.split('_')[:-1]), master_ip, comm_samples)
    elif synth == False:
        create_full_hdfs_file(dataset, master_ip)
    else:
        clean_up_job(original_dataset, master_ip, nodes_info)
        clean_up_job(original_dataset + '_comm', master_ip, nodes_info)
        create_synth_hdfs_file(num_features, master_ip, comm_samples)
        num_features = 10**num_features

    jar = jar_path.split('/')[-1]
    scala_run_spark_job(nodes_info, worker_type, 7077, dataset, 9000, jar, num_features, iterations, log_path, synth)

    return

def run_spark_experiment_wrapper(dataset, nodes_info, worker_type, jar_path, num_features, iterations, log_path, synth, original_dataset):
    # bar = Barrier(1)
    run_spark_experiment(dataset, nodes_info, worker_type, jar_path, num_features, iterations, log_path, synth, original_dataset)
    # while(1):
    #     try:
    #         path_arr = log_path.split('/')
    #         if parse_log('/'.join(path_arr[:-1]), path_arr[-1]) == -1:
    #             raise Exception("UNABLE TO PARSE LOG")
    #         if get_total_log_time('/'.join(path_arr[:-1]), path_arr[-1]) == -1:
    #             raise Exception("UNABLE TO GET TOTAL LOG TIME")
    #         break
    #     except Exception as exc:
    #         print repr(exc)
    #         time_out_check_path = log_path.split('profile_logs')[0] + 'time_out_check'
    #         os.system('rm ' + time_out_check_path)
    #         py_ssh_to_log('', nodes_info[0][0], 'jps', time_out_check_path, True)
    #         f = open(time_out_check_path, 'r')
    #         for line in f:
    #             if 'SparkSubmit' in line or '-- process information unavailable' in line:
    #                 pid = line.split()[0]
    #                 py_ssh('', nodes_info[0][0], 'kill ' + pid)
    #         f.close()

    #         stop_spark(nodes_info[0][0])
    #         start_spark(nodes_info[0][0])
    #         continue
    #     bar = Barrier(1)
    #     run_spark_experiment(dataset, nodes_info, worker_type, jar_path, num_features, iterations, log_path, synth, original_dataset, False, bar)


    return





def main():
    1


if __name__ == "__main__":
    main()

