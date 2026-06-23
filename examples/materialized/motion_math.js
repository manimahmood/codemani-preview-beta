'use strict';

function clamp_unit(x) {
  if ((x < 0)) {
    return 0;
  }
  if ((x > 1)) {
    return 1;
  }
  return x;
}

function smoothstep(x) {
  let y = clamp_unit(x);
  return ((y * y) * (3 - (2 * y)));
}

function blend(a, b, t) {
  let u = smoothstep(t);
  return (a + ((b - a) * u));
}

module.exports = { smoothstep, blend };
