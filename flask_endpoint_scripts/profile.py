import sys, math
sys.path.insert(0,'.')

from setup_cloud import *

def multithread_profile(profile_json):
    manager = Manager()
    ret_dict = manager.dict()
    proc = Process(target=profile,args=(profile_json, ret_dict))
    proc.start()
    pid = proc.pid
    proc.join()
    return dict(ret_dict)


def profile(json_dict, ret_dict):

    profile_start = time()


    unique_time = time_str()
    old_stdout = sys.stdout
    sys.stdout = mystdout = open('profiles/cloud_machine_request_logs/request' + unique_time + '-stdout.log', 'w', buffering=0)

    old_stderr = sys.stderr
    sys.stderr = mystderr = open('profiles/cloud_machine_request_logs/request' + unique_time + '-stderr.log', 'w', buffering=0)

    #BOTO Setup
    conn = start_ec2_boto_connection()

    test = False
    reservation, bid = spot_launch(conn, json_dict['bidPerMachine'], json_dict['machineType'], int(json_dict['numberOfMachines']) + 1)

    old_stdout.write("Working on profile for " + repr(reservation) + '\n')


    profile_dir = 'profiles/' + repr(reservation)
    os.system('mkdir ' + profile_dir)
    os.system('mkdir ' + profile_dir + '/profile_logs')

    sys.stdout = mystdout = open(profile_dir + '/profile_logs/stdout.log', 'w', buffering=0)
    sys.stderr = mystderr = open(profile_dir + '/profile_logs/stderr.log', 'w', buffering=0)

    os.system('mv profiles/cloud_machine_request_logs/request' + unique_time + '-stdout.log ' + profile_dir + '/profile_logs/request-stdout.log')
    os.system('mv profiles/cloud_machine_request_logs/request' + unique_time + '-stderr.log ' + profile_dir + '/profile_logs/request-stderr.log')



    instances = get_instances_from_reservation(reservation)
    instance_ips = get_ips_from_instances(instances)


    dataset, nodes_info = configure_machines_for_spark_job_experiments(json_dict['s3url'], profile_dir, fixed_replication, instance_ips, test)
    master_ip = nodes_info[0][0]


    setup_time_end = time()

    run_spark_experiment_wrapper(dataset + '_comm', nodes_info, json_dict['machineType'], fixed_jar_path, json_dict['features'], real_iterations, profile_dir + '/profile_logs/comm.log', False, dataset)
    run_spark_experiment_wrapper(dataset, nodes_info, json_dict['machineType'], fixed_jar_path, json_dict['features'], real_iterations, profile_dir + '/profile_logs/comp.log', False, dataset)


    profile_time_end = time()


    if int(json_dict['needSynthProfile']) == 1:
        features = int(math.log10(json_dict['features']))
        if features == 0:
            features = 1

        run_spark_experiment_wrapper('synth_' + str(features), nodes_info, json_dict['machineType'], fixed_jar_path, features, synth_iterations, profile_dir + '/profile_logs/synth.log', True, dataset)


        arr = parse_log(profile_dir, 'synth')
        if arr != -1:
            os.system('rm ' + profile_dir + '/profile_logs/synth.log')
            f = open('synth_comm_array_files/synth_' + str(features) + '_' + str(json_dict['numberOfMachines']), 'w')
            f.write(repr(arr))
            f.close()

    synth_profile_time_end = time()

    terminate_instances_from_reservation(conn, reservation)

    ret_dict['reservation'] = repr(reservation)
    ret_dict['save_dir'] = profile_dir
    ret_dict['actual_bid_price'] = bid
    ret_dict['total_price'] = round((int(json_dict['numberOfMachines']) + 1)*float(bid), 2)
    ret_dict['spin_up_time'] = setup_time_end - profile_start
    ret_dict['value'] = 'SUCCESS'
    ret_dict['pid'] = os.getpid()

    print dict(ret_dict)


    sys.stdout = old_stdout
    sys.stderr = old_stderr

    print "Finished profile for ", repr(reservation)

    return






def main():

    profile_json = {'machineType': 'c4.xlarge', 'name': 'susy', 'bidPerMachine': '0.042', 'size_in_bytes': 2100000000, 'budget': '$0.17', 's3url': 's3://susy-data/susy_0', '__v': 0, 'features': 18, 'needSynthProfile': 1, 'samples': 5000000, '_id': '5930d170f95aee0a6194ee7a', 'machine_type': 'c4.xlarge', 'numberOfMachines': '3', 'datasetId': '5930d170f95aee0a6194ee7a', 'size': '2.1 GB'}
    multithread_profile(profile_json)




if __name__ == "__main__":
    main()
