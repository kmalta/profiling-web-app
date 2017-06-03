var express = require('express');
var path = require('path');
var bodyParser = require('body-parser');
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
var app = express();



var mongoose = require('mongoose');
mongoUrl = 'mongodb://localhost:27017/mlwebapp';
mongoose.connect(mongoUrl);
var db = mongoose.connection;


app.set('port', (process.env.PORT || '3000'));
app.set('views', path.resolve('node_src/views'));
app.set('view engine', 'ejs');


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use('/css',express.static(path.resolve('node_src/css')));
app.use('/views',express.static(path.resolve('node_src/views')));
app.use('/data',express.static(path.resolve('node_src/data_files')));
app.use('/javascript',express.static(path.resolve('node_src/javascript')));
app.use('/models',express.static(path.resolve('node_src/models')));
app.use('/bootstrap_css', express.static(path.resolve('node_modules/bootstrap/dist/css')));
app.use('/jquery_js', express.static(path.resolve('node_modules/jquery/dist')));
app.use('/bootstrap_js', express.static(path.resolve('node_modules/bootstrap/dist/js')));


var Dataset = require(path.resolve('node_src/models/dataset.js'));
var Profile = require(path.resolve('node_src/models/profile.js'));
var SynthProfile = require(path.resolve('node_src/models/synth_profile.js'));

var server = app.listen((process.env.PORT || '3000'), function () {
  console.log('Listening on port %d', server.address().port);
});




db.on('error', console.error.bind(console, 'connection error:'));




//WEBSOCKETS
const WebSocket = require('ws');
const wss = new WebSocket.Server({ server });
profile_ws = null;
var wsTimeOutVar;


wss.on('connection', function(_ws) {
  _ws.on('message', function incoming(data) {

    message = safeJSONParse(data);

    if (message['message'] == 'hello') {
      if (message['client'] == 'profile') {
        profile_ws = _ws;
        console.log('Hello Profile Client JS :)')
      }

    }
  });
});




//GETS

app.get('/', function (req, res) {
  res.render(path.resolve('node_src/views/datasets_display/datasets_display.ejs'));
});

app.get('/add_dataset', function (req, res) {
  res.render(path.resolve('node_src/views/dataset_upload/dataset_upload.ejs'));
});

app.get('/datasets_display', function (req, res) {
  res.render(path.resolve('node_src/views/datasets_display/datasets_display.ejs'));
});

app.get('/profile/:token', function(req, res) {
  res.render(path.resolve('node_src/views/profile/profile.ejs'));
});

app.get('/profile', function (req, res) {
  res.render(path.resolve('node_src/views/datasets_display/datasets_display.ejs'));
});

app.get('/back_button', function (req, res) {
  res.render(path.resolve('node_src/views/datasets_display/datasets_display.ejs'));
});

app.get('/get_dataset_db_entries', function(req, res) {
  Dataset.find({}, function (err, datasets) {
    res.send(datasets);
  });  
});






//POSTS



app.post('/process_dataset_from_name', function(req, res) {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", "http://0.0.0.0:8080/process_dataset/" + req.body.dataset, true);
  xhttp.send();
  xhttp.onload = function() {
    res.send(xhttp.responseText)
  }
});

app.post('/get_profile_db_entry', function(req, res) {
  Profile.find({_id: req.body.profile_id}, function (err, profiles) {
    Dataset.find({_id: profiles[0].dataset_id}, function (err, datasets) {
      var xhttp = new XMLHttpRequest();
      xhttp.open("GET", 'http://0.0.0.0:8080/get_bid_price/' + JSON.stringify({data: datasets[0], numberOfMachines: profiles[0].number_of_machines}), true);
      xhttp.send();
      xhttp.onload = function() {
        var data = safeJSONParse(xhttp.responseText);
        res.send(JSON.stringify({profile: profiles[0], bid_return: data}));
      }
    });
  });
});

app.post('/get_bid', function(req, res) {
  Dataset.find({_id: req.body.dataset_id}, function (err, datasets) {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", 'http://0.0.0.0:8080/get_bid_price/' + JSON.stringify({data: datasets[0], numberOfMachines: req.body.number_of_machines}), true);
    xhttp.send();
    xhttp.onload = function() {
      var data = safeJSONParse(xhttp.responseText);
      res.send(JSON.stringify({bid:data['bid'], index:req.body.index}));
    }
  });  
});

app.post('/get_dataset_db_entry', function(req, res) {
  Dataset.find({_id: req.body.dataset_id}, function (err, datasets) {
    res.send(datasets[0]);
  });
});

app.post('/get_dataset_profiles_db_entries', function(req, res) {
  Profile.find({dataset_id: req.body.dataset_id}, function (err, profiles) {
    res.send(profiles);
  });  
});

app.post('/dataset_db_save', function(req, res){
  var dataset = new Dataset({
    name: req.body.name,
    s3url: req.body.url,
    size_in_bytes: req.body.size_in_bytes,
    size: req.body.size,
    samples: req.body.samples,
    features: req.body.features,
    machine_type: req.body.inst_type
  });
  dataset.save(function(err) {
    if (err) throw err;
    console.log('Dataset saved successfully!');
  });

  var log_feats = Math.round(Math.log10(req.body.features));

  if (log_feats == 0) {
    log_feats = 1;
  }
  SynthProfile.find({log_features: log_feats}, function (err, synth_profile) {
    if (synth_profile === undefined || synth_profile.length == 0) {
      var new_synth_profile = new SynthProfile({
        log_features: log_feats,
        machine_counts: Array.apply(null, Array(16)).map(Number.prototype.valueOf,0)
      });
      new_synth_profile.save(function(err) {
        if (err) throw err;
        console.log('New synth profile created and saved!');
      });
    }
  });  
});

app.post('/profile_button_submit', function(req, res) {
  var date = new Date();

  Dataset.find({_id: req.body.datasetId}, function (err, datasets) {
    var dataset = datasets[0];
    var log_feats = Math.round(Math.log10(dataset['features']));

    if (log_feats == 0) {
      log_feats = 1;
    }
    SynthProfile.find({log_features: log_feats}, function (err, synth_profiles) {
      var synth_profile = synth_profiles[0];
      var synth_profile_need = null;
      if (synth_profile.machine_counts[parseInt(req.body.numberOfMachines) - 1] == 0) {
        synth_profile_need = 1;
      }
      else {
        synth_profile_need = 0;
      }

      var profile = new Profile({
        time_submitted: date,
        dataset_id: req.body.datasetId,
        bid_per_machine: parseFloat(req.body.bidPerMachine),
        budget: parseFloat(req.body.budget.split("$")[1]),
        number_of_machines: parseInt(req.body.numberOfMachines),
        machine_type: req.body.machineType,
        profile_finished: 0,
        need_synth_profile: synth_profile_need
      });
      profile.save(function(err) {
        if (err) throw err;
        console.log('Profile saved successfully!');
        req.body.needSynthProfile = synth_profile_need;
        var xhttp = new XMLHttpRequest();
        var json_send = JSON.stringify({dataset: dataset, profile: req.body});
        xhttp.open("GET", 'http://0.0.0.0:8080/submit_profile/' + json_send, true);
        xhttp.send();
        xhttp.onload = function() {
          data = safeJSONParse(xhttp.responseText);
          updateProfile(data, profile._id, dataset, req.body, synth_profile);
        }
        res.redirect('/profile/' + profile._id);
      });

    });
  }); 
});






//PUTS

app.put('/get_profile_results', function(req, res) {
  getProfileFromId(req.body.profile_id);
  res.send(JSON.stringify({message: 'Checked profile for completion.'}));
});






//ERROR HANDLING

// catch 404 and forward to error handler
app.use(function (req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// production error handler
app.use(function (err, req, res, next) {
  res.status(err.status || 500);
  next(err);
});


//HELPER FUNCTIONS

function updateProfile(return_data, profile_id, dataset, profile, synth_profile) {
  var update_profile_params = {
    profile_finished: 1,
    need_synth_profile: 1,
    spin_up_time: return_data.spin_up_time,
    actual_bid_per_machine: return_data.actual_bid_price,
    total_price: return_data.total_price,
    reservation_id: return_data.reservation.split(':')[1].split('\'')[0],
    associated_synth_comm_profile_path: 'synth_' + Math.round(Math.log10(dataset.features)).toString() + 
                                        '_' + profile.numberOfMachines.toString()
  }
  Profile.update({_id:profile_id}, {$set:update_profile_params}, function(err, profile) {
    if (err) throw err;
    console.log('Profile updated successfully!');
    if (synth_profile.machine_counts[parseInt(profile.numberOfMachines) - 1] == 0) {
      var new_machine_counts = synth_profile.machine_counts;
      new_machine_counts[parseInt(profile.numberOfMachines) - 1] = 1;
      SynthProfile.update({log_features: log_feats}, {$set:{machine_counts:new_machine_counts}}, function(err, synth_profile) {
        if (err) throw err;
        console.log('Synth Profile updated successfully!')
        getProfileFromId(profile_id);
      });
    }
    else {
      getProfileFromId(profile_id);
    }
  });
};



function getProfileFromId(profile_id) {
  Profile.find({_id: profile_id}, function (err, profiles) {
    var profile = profiles[0];
    if (profiles.length > 0 && profile.profile_finished == 1) {
      getProfile(profile);
    }
  }); 
}

function getProfile(profile) {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", "http://0.0.0.0:8080/get_profile_results/" + JSON.stringify(profile), true);
  xhttp.send();
  xhttp.onload = function() {
    var data = safeJSONParse(xhttp.responseText);
    sendProfile(JSON.stringify({message: 'return profile data', profile: profile, predictions: data}));
  }
}

function sendProfile(profile_data) {
  wsTimeOutVar = setTimeout(function() { 
    if (profile_ws != null) {
      if (profile_ws.readyState === WebSocket.OPEN) {
        profile_ws.send(profile_data);
      }
      clearTimeout(wsTimeOutVar);
    }
  } , 250);
}

function safeJSONParse(json_str) {
  var json_obj = {};
  try {
      json_obj = JSON.parse(json_str);
  } catch(e) {
      console.log(e); // error in the above string (in this case, yes)!
  }
  return json_obj;
}



module.exports = app;
