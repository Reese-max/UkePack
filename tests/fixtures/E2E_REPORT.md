# E2E Corpus PDF Report

- **Pipeline**: `parse -> suggest_key -> classify -> suggest_strum -> render_pdf`
- **Level**: 1
- **Source type**: public_domain
- **Timing gate**: cold start must stay < 60.0 s, each warm rerender must stay < 7.0 s hard cap, and the corpus warm-run p95 must stay < 5.0 s (`test_e2e_pdf_single_fixture`, `test_corpus_warm_render_p95`).

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
| Cold | 30 | 0.16 | 0.21 | 0.23 | cold < 60.0s |
| Warm | 1 | 0.04 | 0.04 | 0.04 | PASS |

## Per-Fixture Results

| Fixture | Status | Cold (s) | Warm (s) |
|---------|--------|----------|----------|
| alouette | PASS | 0.05 | 0.04 |
| are_you_sleeping | PASS | 0.03 | - |
| au_clair_de_la_lune | PASS | 0.04 | - |
| baa_baa_black_sheep | PASS | 0.10 | - |
| camptown_races | PASS | 0.05 | - |
| clementine | PASS | 0.06 | - |
| farmer_in_the_dell | PASS | 0.06 | - |
| go_tell_aunt_rhody | PASS | 0.07 | - |
| greensleeves | PASS | 0.06 | - |
| happy_birthday | PASS | 0.18 | - |
| hot_cross_buns | PASS | 0.17 | - |
| ive_been_working_on_the_railroad | PASS | 0.16 | - |
| jack_and_jill | PASS | 0.15 | - |
| jingle_bells | PASS | 0.18 | - |
| lightly_row | PASS | 0.16 | - |
| little_brown_jug | PASS | 0.17 | - |
| london_bridge | PASS | 0.21 | - |
| mary_had_a_little_lamb | PASS | 0.20 | - |
| muffin_man | PASS | 0.16 | - |
| oh_susanna | PASS | 0.17 | - |
| old_macdonald_had_a_farm | PASS | 0.23 | - |
| pop_goes_the_weasel | PASS | 0.15 | - |
| row_row_row_your_boat | PASS | 0.14 | - |
| shell_be_coming_round_the_mountain | PASS | 0.15 | - |
| skip_to_my_lou | PASS | 0.17 | - |
| the_mulberry_bush | PASS | 0.18 | - |
| this_old_man | PASS | 0.18 | - |
| three_blind_mice | PASS | 0.14 | - |
| twinkle_twinkle_little_star | PASS | 0.18 | - |
| yankee_doodle | PASS | 0.16 | - |

## Failure Analysis

No failures. All fixtures produced valid PDF output.
