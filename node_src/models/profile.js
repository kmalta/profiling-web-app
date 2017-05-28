var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var profileSchema = new Schema({
    time_submitted: String,
    dataset_id: String,
    spin_up_time: Number,
    actual_bid_per_machine: Number,
    total_price: Number,
    budget: Number,
    cost: Number,
    number_of_machines: Number,
    machine_type: String,
    reservation_id: String,
    associated_synth_comm_profile_path: String,
    profile_finished: Number,
    needs_synth_profile: Number
});

var Profile = mongoose.model('Profile', profileSchema);

module.exports = Profile;