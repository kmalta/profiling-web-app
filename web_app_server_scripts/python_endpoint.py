import sys, requests
sys.path.insert(0,'.')
from functools import wraps
from flask import Flask, request, current_app, redirect, jsonify
from profile_dataset import *
from profile import *
from byteify import *

app = Flask(__name__)


def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)
    return decorated_function


@app.route('/process_dataset/<string:dataset>', methods=['GET'])
@support_jsonp
def get_dataset_info(dataset):
    json_return = get_data_stats(dataset)
    return jsonify(json_return)


@app.route('/submit_profile/<path:profile>', methods=['GET'])
@support_jsonp
def schedule_profile(profile):
    request_json = json_loads_byteified(profile)
    profile_json = dict(request_json['dataset'], **request_json['profile'])
    print profile_json
    #reservation, actual_bid_price, save_dir = euca_profile(profile_json)


    reservation = 'Reservation:r-28f2fe6d'
    actual_bid_price = profile_json['bidPerMachine']
    save_dir = 'profiles/Reservation:r-28f2fe6d'


    ret_dict = {}
    ret_dict['reservation'] = repr(reservation)
    ret_dict['save_dir'] = save_dir
    ret_dict['actual_bid_price'] = actual_bid_price

    ret_dict['comm_time'] = parse_log(save_dir, 'comm')
    ret_dict['comp_time'] = parse_log(save_dir, 'comp')

    return jsonify(ret_dict)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)