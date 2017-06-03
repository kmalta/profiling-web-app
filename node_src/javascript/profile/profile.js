window.onload = function grabProfileEntryInfo() {
    const ws = new WebSocket('ws://localhost:5000');

    ws.onopen = function open() {
        ws.send(JSON.stringify({message: 'hello', client: 'profile'}));

        ws.onmessage = function incoming(event) {
            var data = JSON.parse(event.data);
            if (data['message'] == 'return profile data') {
                update_pricing(data);
                populate_timeseries(data);
                populate_prediction_table(data);
            }
        };
    };



    var url_arr = window.location.href.split('/');
    var profile_id = url_arr[url_arr.length -1].split('-')[0];


    ping_profile_results(profile_id);


    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/get_profile_db_entry", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({profile_id: profile_id}));
    xhttp.onload = function() {
        get_dataset_by_id(xhttp.responseText);
        populate_profile_info_table(xhttp.responseText);
    }
};




function ping_profile_results(profile_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("PUT", "/get_profile_results", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({profile_id: profile_id}));
    xhttp.onload = function() {
        ;
    }
};


function get_dataset_by_id(message) {
    var profile = JSON.parse(message)['profile'];
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/get_dataset_db_entry", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({dataset_id: profile['dataset_id']}));
    xhttp.onload = function() {
        elem_visibility('dataset-info-header', 'block');
        populate_dataset_table(JSON.parse(xhttp.responseText));
    }
};



function populate_profile_info_table(message) {
    var data = JSON.parse(message);
    var profile = data['profile'];
    var values_to_populate = ['$' + profile['budget'].toString(),
                              profile['machine_type'],
                              profile['number_of_machines'],
                              profile['number_of_machines'] + 1,
                              '$' + parseFloat(data['bid_return']['bid']).toString()
                              ]

    for (i = 1; i < values_to_populate.length + 1; i++) {
        var elem = document.getElementById('profile-table-row-col-' + i.toString());
        elem.innerHTML = values_to_populate[i - 1];
    }
    elem_visibility('profile-table', 'table');
};


function update_pricing(message) {
    var data = message.profile;
    elem_visibility('actual-price-loader', 'none');
    var actual_price = document.getElementById('profile-table-row-col-6');
    actual_price.innerHTML = '$' + data['actual_bid_per_machine'].toString();

    elem_visibility('total-price-loader', 'none');
    var actual_price = document.getElementById('profile-table-row-col-7');
    actual_price.innerHTML = '$' + data['total_price'].toString();
};


function createData(arr, offset, value_name) {
    var data = [];
    for (var i = 0; i < arr.length; i++) {
        data.push({
            epoch_num: i + 1 + offset,
            [value_name]: arr[i + offset]
        })
    }
    return data;

};


function populate_timeseries(message) {
    var data = message['predictions'];

    var epoch_chart = d3.timeseries()
              .addSerie(createData(data['comp'], 0, 'real'),
                {x:'epoch_num',y:'real'},
                {interpolate:'monotone',color:"#a6cee3",label:"actual"})
              .addSerie(createData(data['projected'], data.offset - 1, 'predict'),
                  {x:'epoch_num',y:'predict'},
                  {interpolate:'monotone',dashed:true,color:"#e26060",label:"prediction"})
              .width(900)

    epoch_chart("#epoch-chart");
    elem_visibility('epoch-profile-loader', 'none');
    elem_visibility('chart-container', 'block');

    fix_ticks('series-x-axis');
    fix_ticks('slide-x-axis');
};


function fix_ticks(id) {
    var elem = document.getElementById(id);
    var child = elem.children[elem.children.length - 2].children[1];
    child.style = "text-anchor: end";
};

function populate_prediction_table(message) {

    var profile = message['profile']
    var data = message['predictions'];

    var values_to_populate = [
                              roundTo(profile['spin_up_time'], 4),
                              roundTo((data['total_communication_time']/3600)*100, 4),
                              roundTo(data['profiling_time'], 4),
                              roundTo((1 - data['time_saved'])*100, 4),
                              data['projected_epochs']
                              ]

    for (i = 1; i < values_to_populate.length + 1; i++) {
        var elem = document.getElementById('profile-prediction-row-col-' + i.toString());
        elem.innerHTML = values_to_populate[i - 1];
    }
    elem_visibility('profile-prediction-div', 'block')
    elem_visibility('profile-prediction-table', 'table');
};

