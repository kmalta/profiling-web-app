window.onload = function grabProfileEntryInfo() {
    var url_arr = window.location.href.split('/');
    var profile_id = url_arr[url_arr.length -1];
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/get_profile_db_entry", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.send('data=' + JSON.stringify({profile_id: profile_id}));
    xhttp.onload = function() {
        get_dataset_by_id(xhttp.responseText);
        populate_profile_info_table(xhttp.responseText);
    }

    console.log("Start next query")
    var xhttp2 = new XMLHttpRequest();
    xhttp2.open("POST", "/get_profile_results", true);
    xhttp2.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp2.send('data=' + JSON.stringify({profile_id: profile_id}));
    xhttp2.onload = function() {
        console.log(xhttp2.responseText);
    }
};


function get_dataset_by_id(message) {
    var data = JSON.parse(message);
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/get_dataset_db_entry", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhttp.send('data=' + JSON.stringify({dataset_id: data['dataset_id']}));
    xhttp.onload = function() {
        elem_visibility('dataset-info-header', 'block');
        populate_dataset_table(JSON.parse(xhttp.responseText));
    }
}



function populate_profile_info_table(message) {

    data = JSON.parse(message);
    var values_to_populate = ['$' + data['budget'].toString(),
                              data['machine_type'],
                              data['number_of_machines'],
                              data['number_of_machines'] + 1,
                              '$' + parseFloat(data['bid_per_machine']).toString()
                              ]

    for (i = 1; i < values_to_populate.length + 1; i++) {
        var elem = document.getElementById('profile-table-row-col-' + i.toString());
        elem.innerHTML = values_to_populate[i - 1];
    }
    elem_visibility('profile-table', 'table');
}
