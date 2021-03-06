import sys, os
sys.path.insert(0,'.')

from setup_cloud import *
from boto_launch_scripts import *
import math



def get_data_stats(cfg_file):
    f = open('data_configs/' + cfg_file + '.cfg', 'r')
    cfgs = f.readlines()
    f.close()

    s3_bucket = cfgs[0].split('=')[1].strip()
    s3_name = cfgs[1].split('=')[1].strip()
    size_in_bytes = int(cfgs[2].split('=')[1].strip())
    samples = int(cfgs[3].split('=')[1].strip())
    features = int(cfgs[4].split('=')[1].strip())

    dataset_dict = {}
    dataset_dict['message'] = 'return profile data'
    dataset_dict['name'] = cfg_file
    dataset_dict['size_in_bytes'] = size_in_bytes
    dataset_dict['samples'] = samples
    dataset_dict['features'] = features
    dataset_dict['num_workers'] = 4;
    dataset_dict['s3url'] = 'https://s3-us-west-1.amazonaws.com/' + s3_bucket + '/' + s3_name



    inst_types = ['c4.xlarge', 'm4.xlarge', 'r4.2xlarge']
    inst_type = inst_types[0]
    if math.log10(features) <= 4 and size_in_bytes < 4e9:
        inst_type = inst_types[0]
    elif math.log10(features) <= 7 and size_in_bytes < 11.5e9:
        inst_type = inst_types[1]
    else:
        inst_type = inst_types[2]


    dataset_dict['machine_type'] = inst_type


    return dataset_dict

def check_synth_profiles(input_json):
    log_feats = str(input_json['log_features'])
    files = os.listdir('synth_comm_array_files')
    filtered_files = [file for file in files if 'synth_' + log_feats in file]
    synth_profiles = [0 for i in range(16)]
    for file in filtered_files:
        synth_profiles[int(file.split('_')[-1]) - 1] = 1
    return {'synth_profiles': synth_profiles}
