import sys, math
sys.path.insert(0,'.')

from multiprocessing import Process
from setup_cloud import *


def profile(json_dict):

    profile_start = time()


    #figure out logging output!
    # file_suff = time_str()
    # sys.stdout = open('output_logs/stdout-log' + file_suff, 'w')
    # sys.stderr = open('output_logs/stderr-log' + file_suff, 'w')


    #BOTO Setup
    conn = start_ec2_boto_connection()



    #TESTING CODE:
    reservation_id = 'r-3b3a8ea5'
    reservations = get_reservations(conn)
    reservation = reservations[[str(res.id) for res in reservations].index(reservation_id)]
    bid = float(json_dict['bidPerMachine'])
    os.system('rm -rf profiles/' + repr(reservation) + '/profile_logs')

    test = False
    #reservation, bid = spot_launch(conn, json_dict['bidPerMachine'], json_dict['machineType'], int(json_dict['numberOfMachines']) + 1)



    instances = get_instances_from_reservation(reservation)
    instance_ips = get_ips_from_instances(instances)

    profile_dir = 'profiles/' + repr(reservation)
    os.system('mkdir ' + profile_dir)
    os.system('mkdir ' + profile_dir + '/profile_logs')


    # #Get Cluster data structure
    dataset, nodes_info = configure_machines_for_spark_job_experiments(json_dict['s3url'], profile_dir, fixed_replication, instance_ips, test)
    master_ip = nodes_info[0][0]


    setup_time_end = time()

    run_spark_experiment_wrapper(dataset + '_comm', nodes_info, json_dict['machineType'], fixed_jar_path, json_dict['features'], fixed_iterations, profile_dir + '/profile_logs/comm.log', False, dataset)
    run_spark_experiment_wrapper(dataset, nodes_info, json_dict['machineType'], fixed_jar_path, json_dict['features'], fixed_iterations, profile_dir + '/profile_logs/comp.log', False, dataset)


    profile_time_end = time()


    if int(json_dict['needSynthProfile']) == 1:
        features = int(math.log10(json_dict['features']))
        if features == 0:
            features = 1

        run_spark_experiment_wrapper('synth_' + str(features), nodes_info, json_dict['machineType'], fixed_jar_path, features, 1000000, profile_dir + '/profile_logs/synth.log', True, dataset)


        arr = parse_log(profile_dir, 'synth')
        os.system('rm ' + profile_dir + '/profile_logs/synth.log')
        f = open('synth_comm_array_files/synth_' + str(features) + '_' + str(json_dict['numberOfMachines']), 'w')
        f.write(repr(arr))
        f.close()

    synth_profile_time_end = time()

    #terminate_instances_from_reservation(conn, reservation)

    ret_dict = {}
    ret_dict['reservation'] = repr(reservation)
    ret_dict['save_dir'] = profile_dir
    ret_dict['actual_bid_price'] = bid
    ret_dict['total_price'] = round((int(json_dict['numberOfMachines']) + 1)*float(bid), 2)
    ret_dict['spin_up_time'] = setup_time_end - profile_start

    print repr(ret_dict)
    return ret_dict





def main():

    profile_json = {'machineType': 'c4.xlarge', 'name': 'susy', 'bidPerMachine': '0.042', 'size_in_bytes': 2100000000, 'budget': '$0.17', 's3url': 's3://susy-data/susy_0', '__v': 0, 'features': 18, 'needSynthProfile': 0, 'samples': 5000000, '_id': '5930d170f95aee0a6194ee7a', 'machine_type': 'c4.xlarge', 'numberOfMachines': '3', 'datasetId': '5930d170f95aee0a6194ee7a', 'size': '2.1 GB'}
    profile(profile_json)




if __name__ == "__main__":
    main()
