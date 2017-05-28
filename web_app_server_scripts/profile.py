import sys, math
sys.path.insert(0,'./')

from multiprocessing import Process
from setup_cloud import *
from process_results import *


def euca_profile(json_dict):

    #FIXED VALUES
    jar_path = 'spark_job_files/log_reg_explicit_parallelism/target/scala-2.11/log-reg-explicit-parallelism_2.11-1.0.jar'
    iterations = 50
    replication = 3

    profile_start = time()

    #figure out logging output!
    # file_suff = time_str()
    # sys.stdout = open('output_logs/stdout-log' + file_suff, 'w')
    # sys.stderr = open('output_logs/stderr-log' + file_suff, 'w')


    #BOTO Setup
    conn = start_ec2_boto_connection()



    #TESTING CODE:
    # reservation_id = 'r-2e8cbffb'
    # reservations = get_reservations(conn)
    # reservation = reservations[[str(res.id) for res in reservations].index(reservation_id)]
    # bid = float(json_dict['bidPerMachine'])
    # os.system('rm -rf profiles/' + repr(reservation) + '/profile_logs')

    test = False
    reservation, bid = euca_spot_launch_mimicry(conn, json_dict['bidPerMachine'], json_dict['machineType'], int(json_dict['numberOfMachines']) + 1)



    instances = get_instances_from_reservation(reservation)
    instance_ips = get_ips_from_instances(instances)

    profile_dir = 'profiles/' + repr(reservation)
    os.system('mkdir ' + profile_dir)
    os.system('mkdir ' + profile_dir + '/profile_logs')


    # #Get Cluster data structure
    dataset, nodes_info = configure_machines_for_spark_job_experiments(json_dict['s3url'], profile_dir, replication, instance_ips, test)
    master_ip = nodes_info[0][0]


    setup_time_end = time()

    # #create a core variable to change the 4
    comm_samples = int(json_dict['numberOfMachines'])*4


    create_hdfs_files(dataset, master_ip, comm_samples)
    euca_run_spark_experiment(dataset + '_comm', nodes_info, json_dict['machineType'], jar_path, json_dict['features'], iterations, profile_dir + '/profile_logs/comm.log', False)
    euca_run_spark_experiment(dataset, nodes_info, json_dict['machineType'], jar_path, json_dict['features'], iterations, profile_dir + '/profile_logs/comp.log', False)
    clean_up_experiment(dataset, master_ip, nodes_info)
    clean_up_experiment(dataset + '_comm', master_ip, nodes_info)


    profile_time_end = time()


    if int(json_dict['needSynthProfile']) == 1:
        features = int(math.log10(json_dict['features']))
        if features == 0:
            features = 1

        create_synth_hdfs_file(features, master_ip, comm_samples)
        euca_run_spark_experiment('synth_' + str(features), nodes_info, json_dict['machineType'], jar_path, 10**features, 1000000, profile_dir + '/profile_logs/synth.log', True)


        arr = parse_log(profile_dir, 'synth')
        os.system('rm ' + profile_dir + '/profile_logs/synth.log')
        f = open('synth_comm_array_files/synth_' + str(features) + '_' + str(json_dict['numberOfMachines']), 'w')
        f.write(repr(arr))
        f.close()

    synth_profile_time_end = time()
    
    terminate_instances_from_reservation(conn, reservation)


    total_price = round((int(json_dict['numberOfMachines']) + 1)*float(bid), 2)


    ret_dict = {}
    ret_dict['reservation'] = repr(reservation)
    ret_dict['save_dir'] = profile_dir
    ret_dict['actual_bid_price'] = bid
    ret_dict['total_price'] = total_price
    ret_dict['spin_up_time'] = setup_time_end - profile_start

    return ret_dict


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




    return reservation, bid, profile_dir



def main():
    conn = start_ec2_boto_connection()
    reservations = get_reservations(conn)


    clp = sys.argv

    if clp[1] == 'show':
        for i, reservation in enumerate(reservations):
            print str(i + 1) + '.', reservation.id

    if clp[1] == 'terminate':
        if clp[2] == 'all':
            for reservation in reservations:
                terminate_instances_from_reservation(conn, reservation)
        else:

            indices_to_term = [int(item) - 1 for item in clp[2:]]
            for i in indices_to_term:
                terminate_instances_from_reservation(conn, reservations[i])




if __name__ == "__main__":
    main()
