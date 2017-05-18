from price_module.get_bid_API import *
from setup_cloud import *
from boto_launch_scripts import *
import math


inst_types = ['c4.xlarge', 'm4.xlarge', 'r4.2xlarge']


def get_data_stats(cfg_file):
    f = open('data_configs/' + cfg_file + '.cfg', 'r')
    cfgs = f.readlines()
    f.close()

    s3url = cfgs[0].split('=')[1].strip()
    size_in_bytes = int(cfgs[1].split('=')[1].strip())
    samples = int(cfgs[2].split('=')[1].strip())
    features = int(cfgs[3].split('=')[1].strip())

    dataset_dict = {}
    dataset_dict['message'] = 'return profile data'
    dataset_dict['s3url'] = s3url
    dataset_dict['name'] = cfg_file
    dataset_dict['size_in_bytes'] = size_in_bytes
    dataset_dict['samples'] = samples
    dataset_dict['features'] = features
    dataset_dict['num_workers'] = 4;

    inst_type = inst_types[0]
    if math.log10(features) <= 4 and size_in_bytes < 4e9:
        inst_type = inst_types[0]
    elif math.log10(features) <= 7 and size_in_bytes < 11.5e9:
        inst_type = inst_types[1]
    else:
        inst_type = inst_types[2]


    ret_val = get_bid(inst_type, regions, 1)

    dataset_dict['machine_type'] = inst_type
    dataset_dict['bid'] = ret_val['bid']

    return dataset_dict


