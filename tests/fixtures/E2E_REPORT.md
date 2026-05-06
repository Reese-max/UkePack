# E2E Corpus PDF Report

- **Pipeline**: `parse -> suggest_key -> classify -> suggest_strum -> render_pdf`
- **Level**: 1
- **Source type**: public_domain
- **Timing gate**: cold start must stay < 12.0 s, each warm rerender must stay < 5.0 s, and the corpus warm-run p95 must stay < 5.0 s (`test_e2e_pdf_single_fixture`, `test_corpus_warm_render_p95`).

## Summary

| Metric | Value |
|--------|-------|
| Total fixtures | 30 |
| Passed | 30 |
| Failed | 0 |
| Success rate | 100.0% |
| Target | >= 95% |
| Gate | PASS |

## Timing Distribution

| Bucket | Samples | p50 (s) | p95 (s) | p100 (s) | Gate |
|--------|---------|---------|---------|----------|------|
| Cold | 30 | 0.24 | 0.48 | 0.66 | cold < 12.0s |
| Warm | 30 | 0.24 | 0.43 | 0.99 | PASS |

## Per-Fixture Results

| Fixture | Status | Cold (s) | Warm (s) |
|---------|--------|----------|----------|
| alouette | PASS | 0.17 | 0.22 |
| are_you_sleeping | PASS | 0.24 | 0.24 |
| au_clair_de_la_lune | PASS | 0.22 | 0.28 |
| baa_baa_black_sheep | PASS | 0.25 | 0.29 |
| camptown_races | PASS | 0.36 | 0.26 |
| clementine | PASS | 0.20 | 0.23 |
| farmer_in_the_dell | PASS | 0.19 | 0.15 |
| go_tell_aunt_rhody | PASS | 0.21 | 0.16 |
| greensleeves | PASS | 0.20 | 0.34 |
| happy_birthday | PASS | 0.51 | 0.42 |
| hot_cross_buns | PASS | 0.41 | 0.22 |
| ive_been_working_on_the_railroad | PASS | 0.24 | 0.27 |
| jack_and_jill | PASS | 0.24 | 0.19 |
| jingle_bells | PASS | 0.20 | 0.19 |
| lightly_row | PASS | 0.17 | 0.19 |
| little_brown_jug | PASS | 0.19 | 0.17 |
| london_bridge | PASS | 0.31 | 0.43 |
| mary_had_a_little_lamb | PASS | 0.46 | 0.24 |
| muffin_man | PASS | 0.34 | 0.24 |
| oh_susanna | PASS | 0.32 | 0.30 |
| old_macdonald_had_a_farm | PASS | 0.17 | 0.23 |
| pop_goes_the_weasel | PASS | 0.21 | 0.17 |
| row_row_row_your_boat | PASS | 0.21 | 0.42 |
| shell_be_coming_round_the_mountain | PASS | 0.16 | 0.31 |
| skip_to_my_lou | PASS | 0.66 | 0.99 |
| the_mulberry_bush | PASS | 0.38 | 0.38 |
| this_old_man | PASS | 0.31 | 0.28 |
| three_blind_mice | PASS | 0.26 | 0.26 |
| twinkle_twinkle_little_star | PASS | 0.28 | 0.19 |
| yankee_doodle | PASS | 0.23 | 0.15 |

## Failure Analysis

No failures. All fixtures produced valid PDF output.
