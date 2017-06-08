window.onload = grabDBEntryInfo();

function grabDBEntryInfo() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/get_dataset_db_entries", true);
    xhttp.send();
    xhttp.onload = function() {
        createDBTable(JSON.parse(xhttp.responseText));
    }
};

function createDBTable(data) {
    for (var i=0; i < data.length; i++) {
        populate_db_info_table(JSON.stringify(data[i]), i);
    }
    for (var i=0; i < data.length; i++) {
        var row = document.getElementById('profile-table-row-' + i.toString());
        row.onclick = (function(db_entry){
            return function(){
                populate_dataset_table(db_entry);
                grabDatasetProfileEntryInfo(db_entry['_id']);

                elem_visibility('dataset-info-header', 'block');
                elem_visibility('data-table', 'table');
                elem_visibility('dataset-profiles-header', 'block');
                elem_visibility('dataset-profiles-table', 'table');
                elem_visibility('profile-budget-div', 'block');

                var xhttp = new XMLHttpRequest();
                xhttp.open("POST", "/get_bid", true);
                xhttp.setRequestHeader("Content-Type", "application/json");
                xhttp.send(JSON.stringify({dataset_id: db_entry._id, number_of_machines:4}));
                xhttp.onload = function() {
                    var bid = JSON.parse(xhttp.responseText)['bid'];
                    populateHiddenValues(bid, db_entry);
                }

            }
        })(data[i]);
    }
};

function populateHiddenValues(bid, db_entry) {
    var input = document.getElementById('profile-input-budget');
    input.value = '$' + roundTo(5*bid, 3).toString();

    var input = document.getElementById('profile-input-dataID');
    input.value = db_entry['_id']

    var input = document.getElementById('profile-input-bid');
    input.value = bid

    var input = document.getElementById('profile-input-machines');
    input.value = 4

    var input = document.getElementById('profile-input-machineType');
    input.value = db_entry['machine_type']

    var select = document.getElementById('profile-input-machine-count');
    select.value = 4
}

function grabDatasetProfileEntryInfo(dataset_id) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/get_dataset_profiles_db_entries", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({dataset_id: dataset_id}));
    xhttp.onload = function() {
        createDatasetProfileTable(JSON.parse(xhttp.responseText));
    }
};


function createDatasetProfileTable(data) {
    var table = document.getElementById('dataset-profiles-table');
    var table_rows = Array.prototype.slice.call(table.childNodes, 3, table.childNodes.length);
    for (var i=0; i < table_rows.length; i++) {
        table_rows[i].innerHTML = '';
    }
    data.sort(function(x,y){return x['number_of_machines'] - y['number_of_machines']});

    var xhttp_arr = [];
    var html_to_add = table.innerHTML;
    for (var i=0; i < data.length; i++) {
        var temp_xhttp = new XMLHttpRequest()
        xhttp_arr.push(temp_xhttp);

        var row_id = 'dataset-profiles-table-row-' + i.toString();
        html_to_add = html_to_add + "<tr id='" + row_id + "'></tr>";
    }
    table.innerHTML = html_to_add;

    for (var i=0; i < data.length; i++) {

        if (data[i].actual_bid_price == undefined){

        }
        populate_dataset_profiles_table(data[i], i);

        var row = document.getElementById('dataset-profiles-table-row-' + i.toString());
        row.onclick = (function(db_entry){
            if (db_entry['reservation_id'] === undefined) {
                return function(){ window.location.replace('/profile/' + db_entry['_id']) }
            } else {
                return function(){ window.location.replace('/profile/' + db_entry['_id'] + '-' + db_entry['reservation_id']) }
            }
        })(data[i]);

    }

};




function change_profiling_default_amount(num_workers) {

    var input = document.getElementById('dataset-table-row-col-7');
    var dataset_iden = input.innerHTML;

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/get_bid", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify({dataset_id: dataset_iden, number_of_machines:num_workers}));
    xhttp.onload = function() {
        var bid = JSON.parse(xhttp.responseText)['bid'];
        var input = document.getElementById('profile-input-budget');
        input.value = '$' + roundTo(bid*(parseInt(num_workers) + 1), 3).toString();

        var input = document.getElementById('profile-input-machine-count');
        input.value = parseInt(num_workers);

        var input = document.getElementById('profile-input-machines');
        input.value = parseInt(num_workers);
        elem_visibility('profile-budget-div', 'block');
    }

};




function populate_db_info_table(db_entry, idx) {
    db_entry = JSON.parse(db_entry)
    var values_to_populate = [db_entry['name'],
                              db_entry['_id'],
                              db_entry['s3url'],
                              db_entry['size'],
                              db_entry['samples'],
                              db_entry['features'],
                              ]

    var elem = document.getElementById('db-data-table');
    var table = elem.innerHTML;
    var row_id = 'profile-table-row-' + idx.toString();

    var html_to_add = "<tr id='" + row_id + "'>";

    for (i = 1; i < values_to_populate.length + 1; i++) {
        var entry_id = 'profile-table-row-col-' + idx.toString() + '-' + i.toString();
        html_to_add = html_to_add + "<td id='" + entry_id + "'>" + values_to_populate[i - 1] + "</td>"
    }
    html_to_add = html_to_add + "</tr>"
    elem.innerHTML = table + html_to_add

};


function populate_dataset_profiles_table(profile_db_entry, idx) {
    var bid = profile_db_entry.actual_bid_per_machine;
    if (bid == undefined) {
        bid = 'Profile Not Complete'
    }
    else {
        bid = '$' + bid.toString();
    }
    var values_to_populate = [profile_db_entry['number_of_machines'],
                              bid,
                              '$' + profile_db_entry['budget'],
                              profile_db_entry['machine_type'],
                              profile_db_entry['_id']
                              ]

    var elem = document.getElementById('dataset-profiles-table');
    var table_row = document.getElementById('dataset-profiles-table-row-' + idx.toString());
    var row_id = 'dataset-profiles-table-row-' + idx.toString();


    html_to_add = "";
    for (i = 1; i < values_to_populate.length + 1; i++) {
        var entry_id = 'dataset-profiles-table-row-col-' + idx.toString() + '-' + i.toString();
        html_to_add = html_to_add + "<td id='" + entry_id + "'>" + values_to_populate[i - 1] + "</td>"
    }
    table_row.innerHTML = html_to_add;
};

