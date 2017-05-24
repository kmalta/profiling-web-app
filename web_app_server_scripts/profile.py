import sys, os
sys.path.insert(0,'./')


from setup_cloud import *


def parse_log(save_dir, log_type):
    f = open(save_dir + '/profile_logs/' + log_type + '.log', 'r')

    time_array = []
    for line in f:
        if ': Job' in line:
            time_array.append(float(line.split()[-2]))

    return time_array[3:]



def euca_profile(json_dict):


    #BOTO Setup
    conn = start_ec2_boto_connection()
    reservation, bid = euca_spot_launch_mimicry(conn, json_dict['bidPerMachine'], json_dict['machineType'], json_dict['numberOfMachines'])
    instances = get_instances_from_reservation(reservation)
    instance_ips = get_ips_from_instances(instances)
    print "IPs:", repr(instance_ips)

    profile_dir = 'profiles/' + repr(reservation)

    os.system('mkdir ' + profile_dir)
    #os.system('mkdir ' + profile_dir + '/temp_files')
    os.system('mkdir ' + profile_dir + '/profile_logs')

    #FIXED VALUES
    jar_path = 'spark_job_files/log_reg_explicit_parallelism/target/scala-2.11/log-reg-explicit-parallelism_2.11-1.0.jar'
    iterations = 50
    replication = 3

    #Get Cluster data structure
    dataset, nodes_info = configure_machines_for_spark_job_experiments(json_dict['s3url'], profile_dir, replication, instance_ips)
    master_ip = nodes_info[0][0]

    print "MACHINES STARTED!!"

    #create a core variable to change the 4
    comm_samples = int(json_dict['numberOfMachines'])*4 - 4
    create_hdfs_files(dataset, master_ip, comm_samples)
    print "Created HDFS Files"
    euca_run_spark_experiment(dataset + '_comm', nodes_info, json_dict['machineType'], jar_path, json_dict['features'], iterations, profile_dir + '/profile_logs/comm.log')
    euca_run_spark_experiment(dataset, nodes_info, json_dict['machineType'], jar_path, json_dict['features'], iterations, profile_dir + '/profile_logs/comp.log')
    

    print profile_dir + '/profile_logs'

    clean_up_experiment(dataset, master_ip, nodes_info)
    clean_up_experiment(dataset + '_comm', master_ip, nodes_info)


    #IF COMM PROFILE DOES NOT EXIST
    # if json_dict['needs_comm_profile'] == True:
    #     synth_suffix = str(int(math.log10(json_dict['features'])))
    #     #CREATE BUCKET
    #     #CREATE SYNTHETIC DATASET
    #     #ADD SYNTHETIC DATASET
    #     synth_url = 's3://synth-datasets/synth_data_'+ synth_suffix
    #     synth_dataset = ''
    #     create_hdfs_file(dataset, master_ip)



    return reservation, bid, profile_dir


def aws_profile(json_dict):

    #BOTO Setup
    conn = start_ec2_boto_connection()
    reservation, bid = aws_spot_launch_mimicry(conn, json_dict['bidPerMachine'], json_dict['machineType'], json_dict['numberOfMachines'])
    instances = get_instances_from_reservation(reservation)
    instance_ips = get_ips_from_instances(instances)
    print "IPs:", repr(instance_ips)

    profile_dir = 'profiles/' + repr(reservation)

    os.system('mkdir ' + profile_dir)
    #os.system('mkdir ' + profile_dir + '/temp_files')
    os.system('mkdir ' + profile_dir + '/profile_logs')

    #FIXED VALUES
    jar_path = 'spark_job_files/log_reg_explicit_parallelism/target/scala-2.11/log-reg-explicit-parallelism_2.11-1.0.jar'
    iterations = 50
    replication = 3

    #Get Cluster data structure
    dataset, nodes_info = configure_machines_for_spark_job_experiments(json_dict['s3url'], profile_dir, replication, instance_ips)
    master_ip = nodes_info[0][0]

    print "MACHINES STARTED!!"

    #create a core variable to change the 4
    comm_samples = int(json_dict['numberOfMachines'])*4 - 4
    create_hdfs_files(dataset, master_ip, comm_samples)
    print "Created HDFS Files"
    aws_run_spark_experiment(dataset + '_comm', nodes_info, json_dict['machineType'], jar_path, json_dict['features'], iterations, profile_dir + '/profile_logs/comm.log')
    aws_run_spark_experiment(dataset, nodes_info, json_dict['machineType'], jar_path, json_dict['features'], iterations, profile_dir + '/profile_logs/comp.log')
    

    print profile_dir + '/profile_logs'

    clean_up_experiment(dataset, master_ip, nodes_info)
    clean_up_experiment(dataset + '_comm', master_ip, nodes_info)

    terminate_instances_from_reservation(conn, reservation)


    #IF COMM PROFILE DOES NOT EXIST
    # if json_dict['needs_comm_profile'] == True:
    #     synth_suffix = str(int(math.log10(json_dict['features'])))
    #     #CREATE BUCKET
    #     #CREATE SYNTHETIC DATASET
    #     #ADD SYNTHETIC DATASET
    #     synth_url = 's3://synth-datasets/synth_data_'+ synth_suffix
    #     synth_dataset = ''
    #     create_hdfs_file(dataset, master_ip)



    return reservation, bid, profile_dir



def main():
    conn = start_ec2_boto_connection()
    reservations = get_reservations(conn)
    for reservation in reservations:
        terminate_instances_from_reservation(conn, reservation)

    # #mock profile
    # json_dict = {}
    # json_dict['numberOfMachines'] = 5
    # json_dict['features'] = 28
    # json_dict['machineType'] = 'm4.xlarge'
    # json_dict['samples'] = 11000000
    # json_dict['s3url'] = 's3://susy-data/susy_0'
    # json_dict['bidPerMachine'] = .35


    # reservation, bid, profile_dir = euca_profile(json_dict)
    # terminate_instances_from_reservation(conn, reservation)



if __name__ == "__main__":
    main()
