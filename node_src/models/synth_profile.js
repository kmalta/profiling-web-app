var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var synthProfileSchema = new Schema({
    log_features: Number,
    machine_counts: [Number]
});

var SynthProfile = mongoose.model('SynthProfile', synthProfileSchema);

module.exports = SynthProfile;