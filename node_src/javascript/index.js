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








app.post('/process_dataset_from_name', function(req, res) {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", "http://0.0.0.0:8080/process_dataset/" + JSON.parse(req.body.data).dataset, true);
  xhttp.send();
  xhttp.onload = function() {
    res.send(xhttp.responseText)
  }
});



app.post('/dataset_db_save', function(req, res){
  var dataset_json = JSON.parse(req.body.data);
  var dataset = new Dataset({
    name: dataset_json['name'],
    s3url: dataset_json['url'],
    size_in_bytes: dataset_json['size_in_bytes'],
    size: dataset_json['size'],
    samples: dataset_json['samples'],
    features: dataset_json['features'],
    machine_type: dataset_json['inst_type']
  });
  dataset.save(function(err) {
    if (err) throw err;
    console.log('Dataset saved successfully!');
  });

  var log_feats = Math.round(Math.log10(dataset_json['features']));

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

  Dataset.find({_id: req.body.datasetID}, function (err, datasets) {
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
        dataset_id: req.body.datasetID,
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
      });

      req.body['needSynthProfile'] = synth_profile_need;
      var xhttp = new XMLHttpRequest();
      var json_send = JSON.stringify({dataset: dataset, profile: req.body});
      xhttp.open("GET", 'http://0.0.0.0:8080/submit_profile/' + json_send, true);
      xhttp.send();
      xhttp.onload = function() {
        var data = JSON.parse(xhttp.responseText);
        var update_profile_params = {
          profile_finished: 1,
          need_synth_profile: 1,
          spin_up_time: data['spin_up_time'],
          actual_bid_per_machine: data['actual_bid_price'],
          total_price: data['total_price'],
          comm_profile: data['comm_time'],
          full_profile: data['comp_time'],
          reservation_id: data['reservation'].split(':')[1].split('\'')[0],
          associated_synth_comm_profile_path: 'synth_' + Math.round(Math.log10(datasets[0].features)).toString() + 
                                              '_' + req.body.numberOfMachines.toString()
        }
        Profile.update({_id:profile._id}, {$set:update_profile_params}, function(err, result) {
          if (err) throw err;
        });
        if (synth_profile.machine_counts[parseInt(req.body.numberOfMachines) - 1] == 0) {
          var new_machine_counts = synth_profile.machine_counts;
          new_machine_counts[parseInt(req.body.numberOfMachines) - 1] = 1;
          SynthProfile.update({log_features: log_feats}, {$set:{machine_counts:new_machine_counts}}, function(err, result) {
            if (err) throw err;
          });
        }
      }
      res.redirect('/profile/' + profile._id);
    });
  }); 
});



app.post('/get_profile_db_entry', function(req, res) {
  var profile_id = JSON.parse(req.body.data).profile_id;
  Profile.find({_id: profile_id}, function (err, profiles) {
    var profile = profiles[0];

    Dataset.find({_id: profile.dataset_id}, function (err, datasets) {
      var dataset = datasets[0];
      var xhttp = new XMLHttpRequest();
      xhttp.open("GET", 'http://0.0.0.0:8080/get_bid_price/' + JSON.stringify({data: dataset, numberOfMachines: profile['number_of_machines']}), true);
      xhttp.send();
      xhttp.onload = function() {
        var data = JSON.parse(xhttp.responseText);
        res.send(JSON.stringify({profile: profile, bid_return: data}));
      }
    });
  });
});

app.post('/get_bid', function(req, res) {
  var input = JSON.parse(req.body.data)
  var dataset_id = input.dataset_id;
  var number_of_machines = input.number_of_machines;
  Dataset.find({_id: dataset_id}, function (err, datasets) {
    var dataset = datasets[0];
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", 'http://0.0.0.0:8080/get_bid_price/' + JSON.stringify({data: dataset, numberOfMachines: number_of_machines}), true);
    xhttp.send();
    xhttp.onload = function() {
      var data = JSON.parse(xhttp.responseText);
      res.send(JSON.stringify({bid:data['bid'], index:input.index}));
    }
  });  
});

app.post('/get_dataset_db_entry', function(req, res) {
  var input = JSON.parse(req.body.data)
  var dataset_id = input.dataset_id;
  var number_of_machines = input.number_of_machines;
  Dataset.find({_id: dataset_id}, function (err, datasets) {
    res.send(datasets[0]);
  });
});


app.post('/get_dataset_profiles_db_entries', function(req, res) {
  var dataset_id = JSON.parse(req.body.data).dataset_id;
  Profile.find({dataset_id: dataset_id}, function (err, profiles) {
    res.send(profiles);
  });  
});

app.post('/get_profile_results', function(req, res) {
  var profile_id = JSON.parse(req.body.data).profile_id;
  var ret_val = sendProfile(profile_id, res);

  if (ret_val == 0) {
    var refreshId = setInterval(function() {
      Profile.find({_id: profile_id}, function (err, profiles) {
        var profile = profiles[0];
        if (profile.profile_finished == 1) {
          var xhttp = new XMLHttpRequest();
          xhttp.open("GET", "http://0.0.0.0:8080/get_synth_comm/" + JSON.stringify(profile), true);
          xhttp.send();
          xhttp.onload = function() {
            var data = JSON.parse(xhttp.responseText);
            res.send({profile: profile, predictions: data});
            clearInterval(refreshId);
          }
        }
      }); 
    }, 30000);
  }
});



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


function sendProfile(profile_id, res) {
  Profile.find({_id: profile_id}, function (err, profiles) {
    var profile = profiles[0];
    if (profile.profile_finished == 1) {
      var xhttp = new XMLHttpRequest();
      xhttp.open("GET", "http://0.0.0.0:8080/get_synth_comm/" + JSON.stringify(profile), true);
      xhttp.send();
      xhttp.onload = function() {
        var data = JSON.parse(xhttp.responseText);
        res.send({profile: profile, predictions: data});
        return 1;
      }
    }
    else {
      return 0;
    }
  }); 
}


module.exports = app;
