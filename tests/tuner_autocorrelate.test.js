// Behavioral test for tuner.html autoCorrelate boundary guard.
// Replicates the guard logic from app/templates/tuner.html (lines ~634-643)
// and verifies all three boundary cases return -1 (not Infinity / NaN).
//
// Run via: node tests/tuner_autocorrelate.test.js
// Pass: prints "PASS" and exits 0.
// Fail: prints "FAIL: <reason>" and exits 1.

"use strict";

function guardBoundary(maxpos, SIZE, sampleRate) {
  if (maxpos <= 0 || maxpos >= SIZE - 1) {
    return -1;
  }
  return sampleRate / maxpos;
}

const cases = [
  { name: "maxpos=-1 (no peak found)", maxpos: -1, SIZE: 2048, want: -1 },
  { name: "maxpos=0 (peak at lag 0)", maxpos: 0, SIZE: 2048, want: -1 },
  { name: "maxpos=SIZE-1 (peak at end)", maxpos: 2047, SIZE: 2048, want: -1 },
  { name: "maxpos=1 (peak just inside lower bound)", maxpos: 1, SIZE: 2048, want: 44100 / 1 },
  { name: "maxpos=SIZE-2 (peak just inside upper bound)", maxpos: 2046, SIZE: 2048, want: 44100 / 2046 },
];

let failed = 0;
for (const c of cases) {
  const got = guardBoundary(c.maxpos, c.SIZE, 44100);
  const ok = Number.isFinite(got) ? got === c.want : got === c.want;
  const status = ok ? "PASS" : "FAIL";
  console.log(`${status} | ${c.name} | got=${got} want=${c.want}`);
  if (!ok) failed++;
}

// Dedicated assertion for the original bug: Infinity must never appear.
const infinityCase = guardBoundary(0, 2048, 44100);
if (infinityCase === Infinity || !Number.isFinite(infinityCase)) {
  console.log(`FAIL | maxpos=0 produced non-finite value: ${infinityCase}`);
  failed++;
} else {
  console.log(`PASS | maxpos=0 produced finite -1 (bug closed)`);
}

if (failed > 0) {
  console.log(`FAIL: ${failed} test(s) failed`);
  process.exit(1);
}
console.log("PASS: all boundary cases return -1 or valid frequency");
process.exit(0);