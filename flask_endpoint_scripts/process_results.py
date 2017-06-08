import sys
sys.path.insert(0,'.')

import ast
import numpy as np
from time import sleep, gmtime, strftime
from dateutil import parser

from py_command_line_wrappers import *



def time_str():
    return strftime("-%Y-%m-%d-%H-%M-%S", gmtime())

def parse_log(save_dir, log_type):
    try:
        f = open(save_dir + '/profile_logs/' + log_type + '.log', 'r')
        time_array = []
        for line in f:
            if 'DAGScheduler: Job' in line:
                time_array.append(float(line.split()[-2]))
        return time_array[3:]
    except Exception as e:
        print "ERROR:", repr(e)
        print log_type
        print line
        return -1


def safe_split(line):
    left = line.split('INFO')[0]
    time_arr = left.split()[-2:]
    time_arr[0] = time_arr[0][-8:]
    return ' '.join(time_arr)


def get_total_log_time(save_dir, log_type):
    try:
        f = open(save_dir + '/profile_logs/' + log_type + '.log', 'r')
        first_time_str = ''
        last_time_str = ''
        first_line = ''
        last_line = ''
        for line in f:
            if 'Running Spark version ' in line:
                first_time_str = ' '.join(line.split()[:2])
                first_line = line
            if 'Deleting directory /mnt/spark/' in line:
                last_time_str = safe_split(line)
                last_line = line

        first_time = parser.parse(first_time_str)
        last_time = parser.parse(last_time_str)
        seconds = (last_time - first_time).total_seconds()
        return seconds
    except Exception as e:
        print "ERROR:", repr(e)
        print log_type
        print first_line
        print last_line
        return -1

def smooth_synth_close(synth_close):
    for i, elem in enumerate(synth_close):
        if elem <= 0:
            synth_close[i] = synth_close[i - 1]
            elem = synth_close[i - 1]
        elif i > 100 and elem > 5*synth_close[i-1]:
            synth_close[i] = np.median(synth_close[i - 10: i - 1])

    return synth_close


def compute_projection(real_comm, real_full, synth_close, comp_overheads):


    synth_close = smooth_synth_close(synth_close)

    print "Length of synth close:", len(synth_close)


    epochs_profiled = min(min(len(real_full), len(real_comm)), len(synth_close))
    real_full = real_full[:epochs_profiled]
    real_comm = real_comm[:epochs_profiled]

    epoch_window = min(10, epochs_profiled - 3)

    diff_close_profiled = [x - y for x,y in zip(real_comm, synth_close[:epochs_profiled])]
    comm_median = np.median(diff_close_profiled[-epoch_window:])
    projected_comm = real_comm + [comm_median + synth_close[j + epochs_profiled] for j in range(len(synth_close) - epochs_profiled)]


    real_diff_profiled = [x - y for x,y in zip(real_full, real_comm)]
    median = np.median(real_diff_profiled[-epoch_window:])
    projected = real_full + [median + projected_comm[j + epochs_profiled] for j in range(len(synth_close) - epochs_profiled)]

    projection_time = sum(real_comm) + sum(real_full)

    print "comp overheads:", repr(comp_overheads)
    print "projected length:", repr(len(projected))

    accum = 0
    for i in range(len(projected)):
        if i > 100 and projected[i] > 5*projected[i-1]:
            projected[i] = np.median(projected[i - 10: i - 1])
        accum += projected[i]
        if accum > synth_max_time:
            return epochs_profiled, projected[:i + 1]

    return epochs_profiled, projected




def compute_profile_predictions(profile_json):
    path = profile_json['associated_synth_comm_profile_path']
    f = open('synth_comm_array_files/' + path, 'r')
    synth_profile = ast.literal_eval(f.readlines()[0])
    f.close()

    real_comm = parse_log('profiles/Reservation:' + profile_json['reservation_id'], 'comm')
    real_full = parse_log('profiles/Reservation:' + profile_json['reservation_id'], 'comp')


    full_time = get_total_log_time('profiles/Reservation:' + profile_json['reservation_id'], 'comp')
    comm_time = get_total_log_time('profiles/Reservation:' + profile_json['reservation_id'], 'comm')
    comp_overheads = full_time - sum(real_full)

    print "ABOUT TO PROCESS RESULTS!!"
    offset, projected_values = compute_projection(real_comm, real_full, synth_profile, comp_overheads)

    ret_dict = {}
    ret_dict['algorithmic_overheads'] = comp_overheads
    ret_dict['comp'] = real_full
    ret_dict['projected'] = projected_values
    ret_dict['offset'] = offset
    ret_dict['projected_epochs'] = len(projected_values)
    ret_dict['profiling_time'] = full_time + comm_time
    ret_dict['total_communication_time'] = sum(synth_profile[:len(projected_values)])
    ret_dict['time_saved'] = float(full_time + comm_time)/sum(projected_values)

    return ret_dict


def main():
    # test_json = {}

    # reservation = 'r-28f2fe6d'
    # path = 'synth_1_4'

    # test_json['reservation_id'] = reservation
    # test_json['associated_synth_comm_profile_path'] = path

    # compute_profile_predictions(test_json)

    parse_log('/Users/Kevin/profiling-web-app/profiles/Reservation:r-9a20cbb9', 'synth')
    #parse_log('/Users/Kevin/profiling-web-app/profiles/Reservation:r-a7670c64', 'synth')

if __name__ == "__main__":
    main()