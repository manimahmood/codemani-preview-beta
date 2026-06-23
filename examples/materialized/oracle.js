'use strict';
const assert = require('assert');
const scoring = require('./scoring.js');
const reward = scoring.reward_score(0.2, 0.8, 0.4);
const pressure = scoring.zone_pressure(0.25, 0.7);
assert(Math.abs(reward - 0.648) < 1e-12);
assert(Math.abs(pressure - 0.8032484375) < 1e-12);
console.log(JSON.stringify({status: 'PASS', reward, pressure}));
