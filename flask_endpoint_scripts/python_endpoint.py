import sys, requests, ast
sys.path.insert(0,'.')
from functools import wraps
from flask import Flask, request, current_app, redirect, jsonify
from price_module.get_bid_API import *
from dataset_information import *
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


@app.route('/submit_profile/<path:profile_str>', methods=['GET'])
@support_jsonp
def schedule_profile(profile_str):
    request_json = json_loads_byteified(profile_str)
    profile_json = dict(request_json['dataset'], **request_json['profile'])
    ret_dict = multithread_profile(profile_json)
    print repr(ret_dict)
    return jsonify(ret_dict)

@app.route('/get_profile_results/<path:profile_str>', methods=['GET'])
@support_jsonp
def compute_profile(profile_str):
    profile_json = json_loads_byteified(profile_str)
    ret_json = compute_profile_predictions(profile_json)
    return jsonify(ret_json)

@app.route('/get_bid_price/<path:bid_info>', methods=['GET'])
@support_jsonp
def get_bid_info(bid_info):
    request_json = json_loads_byteified(bid_info)
    bid_json = dict(request_json['data'])
    ret_json = get_bid_wrapper(bid_json, request_json['numberOfMachines'])
    return jsonify(ret_json)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True)