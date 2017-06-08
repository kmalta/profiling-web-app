import sys, os
sys.path.insert(0,'.')

from flask_endpoint_scripts.boto_launch_scripts import *
from process_results import *
from synchronization_functions import *



def create_etc_hosts_file(instances, working_dir):
    f = open(working_dir + '/hosts_file', 'w')
    f.write('127.0.0.1 localhost\n')
    f.write(get_priv_ip(instances[0]) + ' master' + '\n')
    for i in range(1, len(instances)):
        f.write(get_priv_ip(instances[i])+ ' slave' + str(i) + '\n')
    f.close()


def setup_passwordless_ssh(master_instance, working_dir):
    cmd_arr = ['source ~/scripts/master_passwordless_ssh.sh', remote_pem_path, get_ip(master_instance)]
    py_ssh_to_log('', get_ip(master_instance), ' '.join(cmd_arr), working_dir + '/profile_logs/remote_stdout.log', True)


def configure_master_node(instances, replication, working_dir):
    setup_passwordless_ssh(instances[0], working_dir)

    cmd_arr = ['source', 'scripts/namenode_env_vars.sh', str(replication), str(len(instances) - 1)]
    py_ssh_to_log('', get_ip(instances[0]), ' '.join(cmd_arr), working_dir + '/profile_logs/remote_stdout.log', True)

def configure_slave_node(instances, slave_instance, replication, working_dir):
    cmd_arr = ['source', 'scripts/datanode_env_vars.sh', str(replication), str(len(instances) - 1)]
    py_ssh_to_log('', get_ip(slave_instance), ' '.join(cmd_arr), working_dir + '/profile_logs/remote_stdout.log', True)


def configure_spark(instances, working_dir):
    f = open(working_dir + '/spark_slaves', 'w')
    for inst in instances[1:]:
        f.write(get_ip(inst) + '\n')
    f.close()
    py_scp_to_remote('', get_ip(instances[0]), working_dir + '/spark_slaves', spark_home + '/conf/slaves')


def start_spark(master_instance, working_dir):
    py_ssh_to_log('', get_ip(master_instance), spark_home + '/sbin/start-master.sh', working_dir + '/profile_logs/remote_stdout.log', True)
    py_ssh_to_log('', get_ip(master_instance), spark_home + '/sbin/start-slaves.sh', working_dir + '/profile_logs/remote_stdout.log', True)

def stop_spark(master_instance, working_dir):
    py_ssh_to_log('', get_ip(master_instance), spark_home + '/sbin/stop-slaves.sh', working_dir + '/profile_logs/remote_stdout.log', True)
    py_ssh_to_log('', get_ip(master_instance), spark_home + '/sbin/stop-master.sh', working_dir + '/profile_logs/remote_stdout.log', True)

def move_spark_conf(instances, worker_type, working_dir):
    if working_dir != '':
        for inst in instances:
            cp_str_arr = ['cp', spark_home + '/conf/spark_machine_conf_files/' + cloud + '/' + worker_type + '.conf', spark_home + '/conf/spark-defaults.conf']
            py_ssh_to_log('', get_ip(inst), ' '.join(cp_str_arr), working_dir + '/profile_logs/remote_stdout.log', True)


def get_params(instances, worker_type, working_dir):
    num_cores = len(instances*4)
    if 'r4.2xlarge' in worker_type:
        move_spark_conf(instances, 'r4.2xlarge', working_dir)
        return '48000m', '48000m', '--conf spark.driver.maxResultSize=10g', 2*num_cores
    elif 'm4.xlarge' in worker_type:
        move_spark_conf(instances, 'm4.xlarge', working_dir)
        return '11500m', '11500m', '--conf spark.driver.maxResultSize=7g', num_cores
    else:
        move_spark_conf(instances, 'c4.xlarge', working_dir)
        return '4000m', '4000m', '', num_cores


def get_cores(instances, worker_type):
    t1, t2, t3, num_cores = get_params(instances, worker_type, '')
    return num_cores

def clean_up_job(dataset, master_instance, working_dir):
    py_ssh_to_log('', get_ip(master_instance), '/usr/local/hadoop/bin/hdfs dfs -rm /' + dataset + '; /usr/local/hadoop/bin/hdfs dfs -ls /', working_dir + '/profile_logs/remote_stdout.log', True)


def wait_and_terminate_spark_job(master_instance, synth, start_time, working_dir, log_path):


    time_out_check_path = log_path.split('profile_logs')[0] + 'time_out_check'
    finished_flag = 0
    if synth == False:
        finished_flag = 0
        while(time() < profiling_max_time + start_time):
            if os.path.exists(time_out_check_path):
                os.system('rm ' + time_out_check_path)
            py_ssh_to_log('', get_ip(master_instance), 'jps', time_out_check_path, True)
            f = open(time_out_check_path, 'r')
            output = f.read()
            f.close()
            if 'SparkSubmit' not in output and '-- process information unavailable' not in output:
                finished_flag = 1
                break
            sleep(5)
    else:
        while(time() < synth_max_time + start_time):
            sleep(int(min(synth_max_time)/2), 60)

    if finished_flag == 0:
        os.system('rm ' + time_out_check_path)
        py_ssh_to_log('', get_ip(master_instance), 'jps', time_out_check_path, True)
        f = open(time_out_check_path, 'r')
        readl = f.readlines()
        f.close()
        for line in readl:
            if 'SparkSubmit' in line or '-- process information unavailable' in line:
                pid = line.split()[0]
                py_ssh_to_log('', get_ip(master_instance), 'kill ' + pid, working_dir + '/profile_logs/remote_stdout.log', True)
                while(1):
                    os.system('rm ' + time_out_check_path)
                    py_ssh_to_log('', get_ip(master_instance), 'jps', time_out_check_path, True)
                    f = open(time_out_check_path, 'r')
                    output = f.read()
                    f.close()
                    if 'SparkSubmit' not in output and '-- process information unavailable' not in output:
                        break


def scala_run_spark_job(instances, worker_type, file_name, num_features, iterations, log_path, synth):

    working_dir = '/'.join(log_path.split('/')[:-2])
    local_dir = '--conf spark.local.dir=/mnt/spark/'

    driver_mem, executor_mem, spark_max_result, num_cores = get_params(instances, worker_type, working_dir)

    run_str = [
               spark_home + '/bin/spark-submit',
               '--verbose',
               '--master', 'spark://master:7077',
               '--deploy-mode client ',
               '--driver-memory ' + driver_mem,
               '--executor-memory ' + executor_mem,
               spark_max_result,
               '--num-executors', str(len(instances) - 1),\
               '--conf spark.default.parallelism=' + str(num_cores),
               local_dir,
               jar_pref + jar_name,
               str(num_features), file_name, str(iterations), str(num_cores)
              ]


    print log_path
    print repr(run_str)
    start_time = time()
    py_ssh_to_log('', get_ip(instances[0]), ' '.join(run_str), log_path, False)

    working_dir = '/'.join(log_path.split('/')[:-2])
    wait_and_terminate_spark_job(instances[0], synth, start_time,  working_dir, log_path)


def configure_hadoop(instances, working_dir):
    create_etc_hosts_file(instances, working_dir)
    for i, inst in enumerate(instances):
        py_scp_to_remote('', get_ip(inst), working_dir + '/hosts_file', 'hosts_file')

    configure_nodes(instances, working_dir)





def configure_nodes(instances, working_dir):
    replication = fixed_replication
    if replication < len(instances) - 1:
        replication = len(instances) - 1

    f = open(working_dir + '/slave_pub_ips', 'w')
    for inst in instances[1:]:
        configure_slave_node(instances, inst, replication, working_dir)
        f.write(get_ip(inst) + '\n')
    f.close()

    for inst in instances:
        py_scp_to_remote('', get_ip(inst), working_dir + '/slave_pub_ips', 'aws/slave_pub_ips')
    configure_master_node(instances, replication, working_dir)


def get_dataset(s3url, master_instance, working_dir):
    get_data_arr = ['python scripts/get_s3_file_using_boto.py', s3url, cloud, key_id, secret_key]
    py_ssh_to_log('', get_ip(master_instance), ' '.join(get_data_arr), working_dir + '/profile_logs/remote_stdout.log', True)


def configure_machines_for_spark_job_experiments(instances, s3url, working_dir):

    dataset = s3url.split('/')[-1]

    log_dir = working_dir + '/profile_logs'

    f = open(working_dir + '/master_ip', 'w')
    f.write(get_ip(instances[0]) + '\n')
    f.close()

    get_dataset(s3url, instances[0], working_dir)
    configure_hadoop(instances, working_dir)
    configure_spark(instances, working_dir)
    py_ssh_to_log('', get_ip(instances[0]), 'source scripts/restart_hadoop.sh ' + remote_pem_path, working_dir + '/profile_logs/remote_stdout.log', True)
    start_spark(instances[0], working_dir)

    return dataset



def create_comm_hdfs_file(dataset, master_instance, comm_samples, working_dir):
    py_ssh_to_log('', get_ip(master_instance), 'head -n ' + str(comm_samples) + ' /mnt/' + dataset + ' > /mnt/' + dataset + '_comm; /usr/local/hadoop/bin/hdfs dfs -put /mnt/' + dataset + '_comm /; /usr/local/hadoop/bin/hdfs dfs -ls /', working_dir + '/profile_logs/remote_stdout.log', True)

def create_full_hdfs_file(dataset, master_instance, working_dir):
    py_ssh_to_log('', get_ip(master_instance), '/usr/local/hadoop/bin/hdfs dfs -put /mnt/' + dataset + ' /; /usr/local/hadoop/bin/hdfs dfs -ls /', working_dir + '/profile_logs/remote_stdout.log', True)

def create_synth_hdfs_file(features, master_instance, comm_samples, working_dir):
    dataset = 'synth_' + str(features)
    py_scp_to_remote('', get_ip(master_instance), 'synth_datasets/' + dataset, '/mnt')
    py_ssh_to_log('', get_ip(master_instance), 'head -n ' + str(comm_samples) + ' /mnt/' + dataset + ' > /mnt/' + dataset + '_temp; /usr/local/hadoop/bin/hdfs dfs -put /mnt/' + dataset + '_temp /' + dataset + '; /usr/local/hadoop/bin/hdfs dfs -ls /', working_dir + '/profile_logs/remote_stdout.log', True)


def run_spark_experiment(dataset, instances, worker_type, num_features, iterations, log_path, synth, original_dataset):
    comm_samples = get_cores(instances, worker_type)
    working_dir = '/'.join(log_path.split('/')[:-2])

    if 'comm' in dataset:
        create_comm_hdfs_file('_'.join(dataset.split('_')[:-1]), instances[0], comm_samples, working_dir)
    elif synth == False:
        create_full_hdfs_file(dataset, instances[0], working_dir)
    else:
        clean_up_job(original_dataset, instances[0], working_dir)
        clean_up_job(original_dataset + '_comm', instances[0], working_dir)
        create_synth_hdfs_file(num_features, instances[0], comm_samples, working_dir)
        num_features = 10**num_features

    scala_run_spark_job(instances, worker_type, dataset, num_features, iterations, log_path, synth)

    return

def wait_for_run_to_complete(master_instance, log_path):
    check_path = log_path.split('profile_logs')[0] + 'block_next_run'

    while(1):
        if os.path.exists(check_path):
            os.system('rm ' + check_path)
        py_ssh_to_log('', get_ip(master_instance), 'jps', check_path, True)
        f = open(check_path, 'r')
        output = f.read()
        f.close()
        if 'SparkSubmit' not in output and '-- process information unavailable' not in output:
            break
        sleep(3)
    return


def run_spark_experiment_wrapper(dataset, instances, worker_type, num_features, iterations, log_path, synth, original_dataset):
    run_spark_experiment(dataset, instances, worker_type, num_features, iterations, log_path, synth, original_dataset)
    wait_for_run_to_complete(instances[0], log_path)

def main():
    1


if __name__ == "__main__":
    main()

