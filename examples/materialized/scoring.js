'use strict';

function reward_score(coverage, smoothness, pressure) {
  const smoothstep = require('./motion_math.js').smoothstep;
  const blend = require('./motion_math.js').blend;
  return ((smoothstep(coverage) + smoothstep(smoothness)) - smoothstep(pressure));
}

function zone_pressure(distance, threat) {
  const smoothstep = require('./motion_math.js').smoothstep;
  const blend = require('./motion_math.js').blend;
  let proximity = (1 - smoothstep(distance));
  return blend(proximity, threat, 0.35);
}

module.exports = { reward_score, zone_pressure };
