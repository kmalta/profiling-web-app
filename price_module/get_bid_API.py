import urllib, sys, ast, math, os
from py_command_line_wrappers import *

regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']


def get_cost(num_machines, inst_type):
    ret_dict = get_bid(inst_type, region)
    return ret_dict['bid']*num_machines

def get_times(reg, inst_type):
    url = 'http://128.111.84.183/' + reg + '-' + inst_type + '.html'
    f = urllib.urlopen(url)
    data = f.readlines()
    script_index = -1
    for i, line in enumerate(data):
        if '<script>' in line:
            script_index = i
            break

    time_line = data[script_index + 2]
    cost_line = data[script_index + 3]


    times = ast.literal_eval('[' + time_line.split('[')[1].split(']')[0] + ']')
    costs = ast.literal_eval('[' + cost_line.split('[')[1].split(']')[0] + ']')

    return times, costs


def get_bid(inst_type, regs, hours):

    times = []
    costs = []
    for reg in regs:
        times, costs = get_times(reg, inst_type)
        if times != []:
            break


    hours_cliff_index = -1
    for i, elem in enumerate(times):
        if int(elem) >= hours:
            hours_cliff_index = i
            break

    time = float(times[i])
    price = float(costs[i])

    ret_dict = {}
    ret_dict['inst_type'] = inst_type
    ret_dict['region'] = reg
    ret_dict['bid'] = price
    ret_dict['duration'] = time
    return ret_dict


def get_bid_wrapper(bid_json, machines):

    log_features = int(math.log10(int(bid_json['features'])))
    if log_features == 0:
        log_features = 1


    synth_path = 'synth_comm_array_files/synth_' + str(log_features) + '_' + str(machines)


    duration = .5
    if os.path.isfile(synth_path):
        duration += 1

    ret_val = get_bid(bid_json['machine_type'], [aws_region], duration)
    
    return ret_val


