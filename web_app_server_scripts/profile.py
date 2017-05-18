import sys, os
sys.path.insert(0,'./')


from setup_cloud import *



def profile(json_dict):

    #BOTO Setup
    conn = start_ec2_boto_connection()
    reservation, working_dir = euca_spot_launch_mimicry(conn, json_dict['bidPerMachine'], json_dict['machineType'], json_dict['numberOfMachines'])
    instances = get_instances_from_reservation(reservation)
    instance_ips = get_ips_from_instances(instances)
    print "IPs:", repr(instance_ips)

    #FIXED VALUES
    jar_path = 'spark_job_files/log_reg_explicit_parallelism/target/scala-2.11/log-reg-explicit-parallelism_2.11-1.0.jar'
    iterations = 50
    replication = 3

    #Get Cluster data structure
    dataset, nodes_info = configure_machines_for_spark_job_experiments(json_dict['url'], working_dir, replication, instance_ips)
    master_ip = nodes_info[0][0]

    create_hdfs_file(dataset, master_ip)
    log_path = working_dir + '/profile_logs/'
    run_spark_experiment(experiment, dataset, nodes_info, json_dict['inst_type'], jar_path, json_dict['features'], iterations, log_path)
    clean_up_experiment(dataset, master_ip)


    if json_dict['needs_comm_profile'] == True:
        synth_suffix = str(int(math.log10(json_dict['features'])))
        #CREATE BUCKET
        #CREATE SYNTHETIC DATASET
        #ADD SYNTHETIC DATASET
        synth_url = 's3://synth-datasets/synth_data_'+ synth_suffix
        synth_dataset = ''
        create_hdfs_file(dataset, master_ip)

    return reservation, working_dir



def main():
    conn = start_ec2_boto_connection()
    reservations = get_reservations(conn)
    for reservation in reservations:
        terminate_instances_from_reservation(conn, reservation)

    #mock profile
    json_dict = {}
    json_dict['features'] = 28
    json_dict['inst_type'] = 'm1.large'
    json_dict['samples'] = 11000000
    json_dict['url'] = 's3://higgs-data/higgs'
    json_dict['bid'] = .35

    reservation = profile(json_dict)
    terminate_instances_from_reservation(conn, reservation)



if __name__ == "__main__":
    main()
