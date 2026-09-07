
# UkePack Product Board Audit — 2026-09-08 04:10 (Asia/Taipei)

Repository: Reese-max/UkePack  
Audited default branch: master  
Audited SHA: 436db728300f6679c193eb886af7a2fd672d7fb2  
Evidence boundary: repository files, Git history, issues, branches, and GitHub Actions metadata/logs. No browser, packaged application, live deployment, real child, teacher, parent, or paid-service test was performed.

## Executive Summary

UkePack is an unusually complete early product for converting legally usable MusicXML/MIDI/chord input into child-friendly ukulele practice material. It already contains arrangement rules, three levels, diagrams, printable PDF, slow practice audio, tuner, teacher review, expiring shares, practice logs, Discord delivery, authorization, and a large automated test suite.

This round found one confirmed release-reliability defect and one strategic research opportunity:

1. The latest authorization remediation SHA has red CI because the governance-history parser crashes when a valid recent commit has no body. This passed the Quality Gate and is tracked by [#2](https://github.com/Reese-max/UkePack/issues/2).
2. The plausible market wedge is not another transcription engine or song library. It is a privacy-minimal “workshop pack set” that helps a teacher turn one authorized source into differentiated, printable material for a group. Demand is not proven, so this is a bounded Research Issue, [#3](https://github.com/Reese-max/UkePack/issues/3), with explicit build/no-build thresholds.

The previous P0 authorization finding [#1](https://github.com/Reese-max/UkePack/issues/1) is statically remediated but not VERIFIED FIXED: CI is red and the required two-user non-production runtime matrix plus two consecutive clean rounds are absent.

Decision: INVEST, but simplify the strategy around teacher-reviewed practice-pack production. Fix the release gate before adding account, roster, billing, marketplace, or new instrument scope.

## Project Discovery

| Dimension | Assessment | Evidence |
|---|---|---|
| Product type | AI-assisted ukulele teaching-material generator | CONFIRMED — README, PRD, teacher guide, arrangement/render modules |
| Maturity | Feature-rich beta / pre-production validation | LIKELY — broad implementation and tests; live deployment evidence missing |
| Primary users | Ukulele teachers, parent-child learners, workshop organizers, AI music creators | CONFIRMED in PRD; actual demand UNKNOWN |
| Core task | Convert legal source material into an editable, child-friendly, printable practice pack | CONFIRMED |
| Main value | Teaching-oriented simplification after transcription, not transcription itself | CONFIRMED in PRD |
| Existing moat candidate | Levelled teaching packs, explainable playability, teacher review, legal-use guardrails | LIKELY |
| Largest current weakness | Release truth: latest remediation cannot claim a green CI suite | CONFIRMED by Actions run 34065881117 |
| Security | Capability tokens, project isolation, share containment, CSRF and production fail-closed are present | CONFIRMED statically; runtime UNKNOWN |
| Testing | Ruff and mypy pass; pytest reaches near completion but one governance parser test crashes | CONFIRMED from job log |
| Accessibility | Child-friendly print intent exists; screen reader, keyboard, zoom, contrast, PDF readability runtime tests not found | UNKNOWN |
| Distribution | Web/Render path, export files, expiring share links, Discord bot | CONFIRMED code/docs; production usage UNKNOWN |

Primary evidence reviewed: README.md, PRD.md, BACKLOG.md, MISSION.md, teacher guide, pyproject.toml, CI workflow, authorization implementation/tests, governance parser test, project/share/practice routes, Round-1/Round-2 audits, recent commits, issue comments, open/closed PRs, branches, Actions runs and job logs.

## Competitive Intelligence

Public product pages were checked on 2026-09-08: [Klangio](https://klang.io/), [Chordify](https://chordify.net/), [Yousician](https://yousician.com/), [MuseScore](https://musescore.com/sheetmusic), and [UkuTabs](https://ukutabs.com/).

| Capability | UkePack | Klangio | Chordify | Yousician | MuseScore | UkuTabs |
|---|---|---|---|---|---|---|
| Target user | Teachers, families, workshop creators | Musicians needing transcription | Players following popular songs | Individual learners | Composers/arrangers/community | Ukulele song learners |
| Value proposition | Turn legal notation into teachable child-friendly packs | Audio/YouTube to notation | Synchronized chords and playback | Guided interactive learning | Create/edit/share notation | Large ukulele chord/tab catalog |
| Killer feature | Level 1/2/3 teaching pack plus teacher review | AI multi-instrument transcription | Instant song playback with transpose/simplify | Adaptive lessons and feedback | Powerful notation ecosystem | Ukulele-specific song access |
| Onboarding | Technical beta with source import | Upload audio/URL | Search a song | App lesson path | Desktop/web creation | Search and play |
| UX | Pack workflow; teacher-oriented | Transcription/edit/export | Consumer play-along | Highly guided/mobile | Expert notation UI | Simple catalog pages |
| Automation/AI | Analysis, simplification, arrangement | Core transcription AI | Chord extraction/playback | Adaptive instruction | Growing notation tooling | Limited |
| Integrations/API | MusicXML/MIDI/PDF/Discord | MusicXML/MIDI/Guitar Pro/API | Web/mobile | Mobile/desktop | MusicXML/MIDI/community | Web |
| Mobile | Shared pages likely usable; not verified | Browser/app-dependent | Strong | Strong | Apps/web | Strong web |
| Reliability | Red current CI; runtime pending | Managed service | Managed service | Managed service | Mature ecosystem | Managed content site |
| Security/privacy | Self-hosted capability model | Vendor cloud | Vendor cloud | Accounts/vendor cloud | Accounts/open desktop editor | Public content |
| Pricing | Self-host; business model unvalidated | Free trial plus paid/API | Freemium/Premium | Subscription | Free editor plus paid content/services | Freemium/content |
| Open/closed | Private repo/product code | Closed service | Closed service | Closed service | Open-source editor + closed marketplace services | Closed site |
| Community/distribution | GitHub/direct teacher sharing | Creator/pro transcription market | Large song community | Consumer learning funnel | Large score community | Ukulele search/discovery |
| Main strength | Teacher-ready last mile | Accurate transcription/export | Song immediacy | Curriculum and feedback | Editing depth and interoperability | Catalog breadth |
| Main weakness vs UkePack thesis | Unproven market/onboarding | Not centered on child-ready teaching packs | Copyright/catalog model and limited teacher packaging | Individual curriculum, not custom pack production | Requires manual teaching adaptation | Static catalog, limited differentiation |

Gap classification:

- MUST MATCH: green reproducible releases, safe private projects/shares, readable PDF, import failure recovery, mobile-openable student share, clear copyright state.
- SHOULD BE BETTER: time from MusicXML to teacher-approved pack, level differentiation, plain-language playability explanations, print quality, privacy-minimal distribution.
- DIFFERENTIATOR: one authorized source to three teacher-reviewed levels; combined print/share pack sets; no child account required; reproducible teacher corrections.
- DO NOT COPY: broad consumer song catalog, full AI transcription model, gamified lesson universe, all-instrument support, public marketplace, or full LMS before evidence.

## Competitive Gaps and Opportunities

1. Release evidence is below minimum: the current master SHA is red.
2. UkePack already has many features but has not proven the core time-to-value with real teachers.
3. The teacher/workshop segment is named in the PRD, yet the current flow is project-by-project. Whether batching is valuable is UNKNOWN.
4. Mobile, accessibility, and print/PDF behavior are documented but not runtime verified.
5. Competing on catalogs or interactive curriculum would dilute the product. The narrow opportunity is teacher production workflow.

## Virtual Executive Board

| Role | Independent assessment |
|---|---|
| CEO | If resources allow only three things: restore green CI, validate teacher preparation time-to-value, and prove secure/mobile distribution. Do not build a song marketplace or full LMS. |
| CPO | The question is whether teachers can prepare better material faster, not whether more modules can be added. |
| CTO | CI parser fragility must be fixed without weakening governance. Keep capability authorization centralized. |
| Staff/Principal Engineer | Replace brittle delimiter trimming with a total parser and deterministic fixtures. Reduce history-dependent CI behavior. |
| UX Lead | The main flow should read “import → choose learner level → review → print/share”; hide secondary technical paths. |
| UX Researcher | Synthetic preference is insufficient. Observe at least five teachers preparing real legal-source material. |
| Growth Lead | Teacher templates and pack sets could drive parent/student exposure without a public marketplace. |
| CFO/Business Analyst | Require repeated-use and willingness-to-pay evidence before account/billing infrastructure. |
| Security/Privacy Lead | Avoid collecting child names/contact data; share links must remain revocable and read-only. |
| QA Lead | One red test means no green release claim; add commit-message shape fixtures. |
| SRE Lead | Record exact SHA, CI run, deploy receipt, and smoke result separately. |
| Accessibility Specialist | Validate PDF large text, color independence, keyboard flow, screen readers, and mobile zoom with real runtime. |
| Customer Support Lead | Clarify source-license errors, missing MIDI/ffmpeg, expired shares, token recovery, and print failures. |

Cross-review consensus: FIX #2 first, then execute #3 as research. Minority opinion: build a complete teacher account/roster system immediately. Rejected because it adds child-data, authorization, support, and migration obligations before demand is established.

## 50 Synthetic Personas

These are synthetic simulations, not real participants, market research, browser testing, or proof of usability. A01–F05 are the 30-person regression baseline; G01–J05 are 20 rotating exploration personas.

| ID | Background | Goal | Expectation / Task | Journey | Friction | Result | Comment | Sev | Suggestion |
|---|---|---|---|---|---|---|---|---|---|
| A01 | 8, first-time learner, tablet, parent-assisted | Play chorus | Big simple cues / open shared pack | Link → PDF → first chords | Runtime/mobile unknown | UNKNOWN | Child value depends on legibility | P2 | Test tablet PDF |
| A02 | 10, beginner, slow Wi-Fi | Practice 10 minutes | Fast loading / play slow track | Open → audio → repeat | Network/audio untested | UNKNOWN | Avoid heavy app shell | P2 | Slow-network smoke |
| A03 | 13, some music skill, phone | Try Level 2 | Clear level difference | Open pack → compare patterns | Level distinction static only | PARTIAL | Concept fits | P3 | Comprehension test |
| A04 | 6, small hands, paper-first | Use easy chords | Large diagrams / print | Parent prints → follows | Print size unknown | UNKNOWN | Core product promise | P1 | Real-printer QA |
| A05 | 16, self-directed, laptop | Edit notation later | MusicXML export | Download → MuseScore | Interop not runtime tested | UNKNOWN | Important escape hatch | P2 | Round-trip corpus |
| B01 | 38, parent, low digital skill | Make family song pack | Guided setup | Create → import → level → print | Technical inputs confusing | PARTIAL | May need teacher-first positioning | P2 | Simplify first run |
| B02 | 41, musical parent | Adjust key | Explain recommendation | Import → compare key → choose | Decision wording not tested | PARTIAL | Explainability is valuable | P3 | Test reason text |
| B03 | 35, privacy-conscious parent | Share safely | No child account | Create expiring link | Runtime auth unknown | PARTIAL | Capability approach fits | P1 | Live isolation smoke |
| B04 | 48, printer-dependent parent | Print 4 pages | No clipping/blank page | Preview → print | Guide admits layout issues | FAIL likely | Needs device evidence | P1 | Print matrix |
| B05 | 33, AI-music parent | Use own Suno song | License clarity | Declare source → import → export | Rights depend on plan/territory | PARTIAL | Tool cannot grant rights | P2 | Keep explicit declaration |
| C01 | 29, ukulele teacher, 12 students | Prepare 3 levels | Faster than manual | One source → variants → review | Repeated project handling | FAIL likely | Research #3 | STRATEGIC | Test pack-set prototype |
| C02 | 45, community teacher | Reuse corrections | Teacher templates | Review → save → reuse | Cross-project reuse depth unknown | PARTIAL | Reuse may be moat | P2 | Observe real workflow |
| C03 | 31, remote teacher | Send family links | Revocable links | Generate → send → revoke | Distribution runtime unknown | PARTIAL | Privacy-minimal | P1 | Black-box share test |
| C04 | 39, school teacher | Keep classes separate | Strong isolation | Project A/B token tests | Static tests exist; CI red | PARTIAL | Original P0 improved | P0 | Complete #1 verification |
| C05 | 54, experienced arranger | Override AI | Full teacher control | Review → edit → export | Editing depth not runtime tested | PARTIAL | Do not automate away expertise | P2 | Preserve manual escape |
| D01 | 27, workshop organizer, 30 learners | Print bundles | Batch variants | Prepare → assign → print | No validated batch flow | FAIL likely | Research hypothesis | STRATEGIC | #3 |
| D02 | 42, nonprofit organizer | Low-cost offline activity | No learner accounts | Generate → print → distribute | Strong fit, unproven | PARTIAL | Avoid LMS | P2 | Prototype paper-first |
| D03 | 36, release maintainer | Trust master | Green checks | Inspect latest run | Pytest parser crash | FAIL | Confirmed defect | P1 | #2 |
| D04 | 50, copyright reviewer | Prevent illegal sharing | Clear usage states | Select source → share | Enforcement/runtime unknown | PARTIAL | Strong positioning guard | P1 | License-state smoke |
| D05 | 34, privacy officer | Minimize child data | Pseudonymous/no PII | Review data model | Account roadmap may add PII | PARTIAL | Research must constrain | STRATEGIC | #3 no-PII threshold |
| E01 | 11, dyslexic learner | Read instructions | Plain language/spacing | Open PDF → follow steps | Not tested | UNKNOWN | Child-friendly claim pending | P2 | Reading usability study |
| E02 | 63, low-vision grandparent | Help learner | 200% zoom/high contrast | Open share → zoom | Runtime unknown | UNKNOWN | Must not rely on tiny diagrams | P2 | Zoom/contrast check |
| E03 | 28, motor-impaired teacher | Complete keyboard-only | Accessible controls | Import → review → export | Browser not tested | UNKNOWN | Core authoring flow | P2 | Keyboard audit |
| E04 | 9, color-vision difference | Read chord difficulty | Text/non-color cues | View badges → decide | Static unknown | UNKNOWN | Avoid color-only status | P3 | Visual encoding audit |
| E05 | 40, screen-reader user | Create pack | Semantic forms/errors | Form → import → review | No AT evidence | UNKNOWN | Do not claim compliance | P2 | Screen-reader test |
| F01 | 26, API user | Automate pack generation | Stable API | Create → import → export | Auth migration requires integration proof | PARTIAL | Token boundary is correct direction | P1 | API contract tests |
| F02 | 37, Discord community teacher | Generate in chat | Safe attachment flow | Upload → bot → PDF | Bot authorization/privacy unclear runtime | UNKNOWN | Secondary channel | P2 | Limit scope |
| F03 | 22, Linux self-hoster | Deploy locally | Clear setup | Clone → uv → run | Runtime not executed | UNKNOWN | Docs exist | P3 | Clean-clone smoke |
| F04 | 44, Render operator | Public beta | Fail closed without secret | Deploy → startup | Static guard only | PARTIAL | Needs deployment proof | P0 | Non-prod verification |
| F05 | 32, support volunteer | Diagnose failure | Actionable errors | Bad MusicXML → recover | Error UX not executed | UNKNOWN | Support cost risk | P2 | Invalid-file corpus |
| G01 | 30, music therapist, professional | Adapt simple activities | Ethical scope | Import public-domain → simplify | Product not clinical | PARTIAL | Avoid clinical claims | P2 | Scope statement |
| G02 | 47, special-education teacher | Individualize pacing | Multiple difficulty outputs | One song → 3 packs | Pack assignment unvalidated | PARTIAL | Good research segment | STRATEGIC | Include in #3 |
| G03 | 25, camp instructor, offline venue | Run without network | Printable kit | Pre-build → print → teach | Offline distribution likely strong | PARTIAL | Differentiator | P2 | Test offline pack set |
| G04 | 58, substitute teacher | Use with no training | Five-minute handoff | Open guide → print | Guide is long | FAIL likely | Progressive disclosure needed | P2 | One-page checklist |
| G05 | 34, curriculum designer | Compare versions | Audit teacher edits | Generate → review → export | Version provenance unclear | UNKNOWN | Potential later improvement | P3 | Validate need |
| H01 | 40, AppSec reviewer | Test adjacent IDs | 401/403 before data | Enumerate IDs | Static tests present | PARTIAL | Runtime required | P0 | #1 runtime matrix |
| H02 | 29, CI maintainer | Run suite | Deterministic tests | Push subject-only commit | Parser crashes | FAIL | Exact #2 trigger | P1 | Total parser |
| H03 | 52, SRE | Know deployed SHA | Release receipt | CI → deploy → smoke | Deploy evidence absent | UNKNOWN | Separate gates | P1 | Evidence chain |
| H04 | 31, security reviewer | Approve auth change | Green required CI | Inspect checks | Red current SHA | FAIL | Cannot sign off | P1 | #2 |
| H05 | 38, recovery operator | Preserve projects | Migration/backup | Upgrade → verify | Runtime migration not tested here | UNKNOWN | High consequence | P1 | Staged backup smoke |
| I01 | 24, malicious enumerator model | Read others' projects | Adjacent ID attack | Request IDs without token | Static denial present | PARTIAL | No live exploit attempt | P0 | Two-user black-box |
| I02 | 46, impatient teacher | Finish in 15 minutes | Minimal steps | Import → accept → print | Feature density may overwhelm | FAIL likely | Simplify UI | P2 | Time-on-task study |
| I03 | 35, open-source contributor | Submit governance change | Clear CI feedback | Commit with empty body | Internal crash | FAIL | Actionability poor | P1 | #2 |
| I04 | 43, business owner | Choose subscription | Clear value | Compare manual time | WTP unknown | UNKNOWN | No pricing work yet | STRATEGIC | #3 interviews |
| I05 | 28, interrupted user | Resume safely | No lost project/token | Close → return | Token recovery runtime unknown | UNKNOWN | Capability UX tradeoff | P1 | Recovery scenario |
| J01 | 21, catalog-first consumer | Find pop songs | Huge search catalog | Search title | UkePack not designed for this | FAIL by design | Competitors win | — | Do not copy |
| J02 | 37, Yousician subscriber | Get feedback on playing | Real-time recognition | Play instrument | Explicit non-goal | FAIL by design | Stay focused | — | Do not build now |
| J03 | 33, MuseScore power user | Fine-grained notation | Full editor | Import → advanced edit | UkePack delegates editing | PARTIAL | Interop better than clone | P2 | Maintain MusicXML export |
| J04 | 49, workshop buyer | Approve 20-seat event | Evidence and repeatability | Pilot → compare time | No human study | UNKNOWN | Strategic decision gap | STRATEGIC | #3 |
| J05 | 55, principal engineer | Release securely | Green CI + runtime proof | Review SHA and checks | CI red/runtime missing | FAIL | Highest engineering priority | P1 | #2 then #1 verification |

## Competitor Switching Test

Scenario: “Prepare or learn a beginner ukulele song from legal source material.”

| Choice | Personas | Synthetic Preference Share | Main reason |
|---|---:|---:|---|
| UkePack | 16 | 32% | Teacher review, levelled printable packs, privacy/self-hosting |
| Yousician | 12 | 24% | Guided consumer lessons and interactive feedback |
| Chordify | 9 | 18% | Immediate song playback, transpose and simplification |
| MuseScore | 7 | 14% | Powerful notation editing and interoperability |
| Klangio | 4 | 8% | Fast transcription from audio |
| UkuTabs | 2 | 4% | Ukulele catalog convenience |

This is a simulated preference exercise, not market share or a real survey. UkePack wins only when the job is teacher-prepared, legal-source, differentiated material. It loses consumer discovery and realtime-feedback scenarios by design.

## Red Team

- Persona bias: teachers, privacy, and technical operators are overrepresented relative to casual learners.
- Competitor mismatch: Klangio is upstream transcription; MuseScore is an editing ecosystem; Yousician is curriculum. Feature parity is not the goal.
- Numeric rigor risk: playability scores can look scientific without evidence that they predict a child's success.
- Overengineering risk: account, roster, analytics, billing and messaging could turn a focused pack generator into a weak LMS.
- Growth bias: public sharing or a song marketplace creates moderation and copyright burdens.
- Security bias: capability URLs simplify sharing but can create recovery and leakage support problems.
- Simplification alternative: validate “pack set” as a local/export abstraction before any multi-user account model.
- Removal/de-emphasis: hide Discord, API, MIDI/ffmpeg and advanced paths from first-run teacher flow unless needed.
- CI finding challenge: the failure is in governance tooling, not end-user code. It still passes because it blocks trustworthy release acceptance with deterministic evidence.
- Research finding challenge: synthetic preference cannot justify implementation. #3 therefore requires real participants and supports DO NOT BUILD.

## Findings, Quality Gate and Issue Mapping

### F-01 — Governance commit parser crashes on empty commit body

- Type: RELIABILITY / TECH_DEBT
- Priority: P1
- Evidence: CONFIRMED code plus Actions log
- Trigger: recent monitored governance-file commit with subject and empty body
- Symptom: pytest ValueError, full CI red
- Root cause: entry.strip() removes the trailing unit separator before three-field unpack
- Impact: release/security remediation cannot obtain a green required gate
- Confidence: High
- Effort: Small
- Runtime requirement: CI only
- Quality Gate: PASS
- Mapping: NEW — [#2](https://github.com/Reese-max/UkePack/issues/2)

### F-02 — Validate privacy-minimal workshop pack sets before teacher accounts

- Type: RESEARCH_REQUIRED / DIFFERENTIATOR / COMPETITIVE_GAP
- Priority: STRATEGIC
- Evidence: CONFIRMED target segment and current project flow; LIKELY repetition pain; demand UNKNOWN
- Impact: could establish a narrow moat or prevent an expensive LMS detour
- Confidence: Medium on alignment, Low on demand magnitude
- Effort: Small research; potentially large implementation
- Runtime requirement: real prototype observation
- Quality Gate: PASS as Research
- Mapping: NEW / RESEARCH — [#3](https://github.com/Reese-max/UkePack/issues/3)

### F-03 — Authorization remediation exists but end-to-end acceptance is incomplete

- Type: SECURITY / RELIABILITY
- Priority: P0 lineage
- Evidence: CONFIRMED static remediation and tests; CONFIRMED CI red; deployment runtime UNKNOWN
- Impact: original cross-user data risk is not statically reproducible, but full closure cannot be verified
- Confidence: High static / Unknown deployed
- Quality Gate: PASS as regression update
- Mapping: UPDATED EXISTING — [#1](https://github.com/Reese-max/UkePack/issues/1)
- Status: PARTIALLY FIXED / NEEDS_RUNTIME_VERIFICATION; not reopened because the original static root cause is no longer reproducible

## Rejected Findings

| Candidate | Decision | Reason |
|---|---|---|
| New authorization Issue | REJECTED duplicate | Same root cause as #1; update existing evidence instead |
| Reopen #1 as REGRESSION | REJECTED | Original integer-ID-only authorization is not reproduced on current source |
| Build full teacher LMS now | REJECTED | Demand and privacy contract unvalidated; #3 narrows research |
| Add audio transcription model | REJECTED | Explicit non-goal and Klangio already serves upstream task |
| Add public song marketplace | REJECTED | Copyright, moderation and distribution burden |
| Add all instruments | REJECTED | Violates focused ukulele strategy |
| Claim accessibility defect | REJECTED | No browser/AT/print execution; retain runtime pending |
| Claim 803 tests passed on GitHub | REJECTED | The actual current Actions run failed |
| Remove governance test | REJECTED | Would weaken a deliberate control rather than fix its parser |
| Add realtime performance scoring | REJECTED | High scope; Yousician-style feature copying without evidence |

## Regression Closure

| Issue | Classification | Evidence |
|---|---|---|
| #1 project authorization | PARTIALLY FIXED / NEEDS_RUNTIME_VERIFICATION | Capability boundary/tests exist; current CI red; no two-user deployed matrix or two clean rounds |
| #2 governance parser | STILL REPRODUCIBLE on audited SHA | Actions run 34065881117 fails exactly at the parser |
| #3 workshop pack-set research | NEW / NEEDS_REAL_USER_RESEARCH | Synthetic personas cannot close it |

Verified Fixed Issues: 0.  
Verified subcomponents: Ruff and mypy pass on 436db728; capability checks and regression tests exist statically.  
Runtime Pending: non-production two-user isolation, anonymous rejection, share read-only behavior/revocation, CSRF browser path, token recovery, migration, mobile share, slow network, screen reader, keyboard, zoom, and print output.

## Priority and Roadmap

### NOW

1. FIX #2 without weakening the governance rule; obtain a green Actions run.
2. Complete #1's non-production two-user/auth/share/CSRF runtime matrix.
3. Run real printer and mobile-share smoke tests on the exact release SHA.

### NEXT

1. Execute #3's five-teacher/workshop study with a no-child-PII pack-set prototype.
2. Measure median teacher preparation time, correction count, print defects, and distribution errors.
3. Simplify first-run UI around import → level → review → print/share.

### LATER

- Reusable teacher templates and pack sets only if #3 reaches its threshold.
- Better MusicXML round-trip and version provenance.
- Cost/usage telemetry only if hosted services are introduced.

### DON'T

- Do not build a full LMS, child accounts, messaging, marketplace, broad song catalog, transcription model, or multi-instrument suite now.
- Do not treat synthetic personas as market validation.
- Do not claim production security from static code or a locally reported test count.
- Do not close #2 without a linked successful CI run.

## Difference from Previous Round

- Authorization implementation 436db728 landed after the prior Round-2 audit.
- The original static P0 path is no longer reproduced in reviewed source.
- The exact remediation SHA produced new concrete CI evidence: lint/mypy pass, pytest fails in governance history parsing.
- A new P1 reliability Issue #2 was created.
- Competitor research reframed the product away from transcription/catalog parity toward teacher-prepared pack sets.
- A bounded strategic Research Issue #3 was created instead of implementing a classroom/LMS feature.
- #1 received an evidence-based PARTIALLY FIXED / NEEDS_RUNTIME_VERIFICATION update.

## Decision Memo

- What this product should become: the fastest trustworthy way for a teacher to turn authorized notation into reviewed, differentiated, printable beginner ukulele material.
- Who it should serve: ukulele teachers, parent-child workshop organizers, and advanced parents using legal/self-created/public-domain material.
- Why users choose it: levelled teaching output, teacher review, printable/offline use, practice audio, privacy/self-hosting, and clear legal-use states.
- Why users choose competitors: instant song catalogs, transcription from audio, full notation editing, guided curriculum, mobile feedback, or community scale.
- Biggest competitive gaps: release trust, real teacher validation, mobile/print accessibility evidence, onboarding simplicity.
- Potential moat: teacher correction templates plus privacy-minimal pack sets and evidence that they reduce preparation time.
- Top priorities: green CI, secure runtime proof, preparation-time research, print/mobile quality.
- What NOT to build: transcription model, general LMS, public marketplace, all instruments, realtime gamified curriculum.
- Features worth removing/de-emphasizing: secondary Discord/API/MIDI/ffmpeg paths from first-run navigation if analytics show they distract.
- Biggest risks: feature bloat, copyright misuse, child-data collection, capability-token loss/leakage, misleading playability scores, red release gate.
- Next experiments: parser fixtures and green CI; two-user deployed auth smoke; five-teacher pack-set observation; print/mobile/accessibility matrix.
- Portfolio decision: INVEST — constrained to focused teacher workflow and reliability.

## Portfolio CEO Review

UkePack overlaps with ppt-studio/minideck in export-oriented document generation and with cyber-prep-coach/police exam products in educational progress tracking. Reuse opportunities: a common document provenance/export receipt, capability-link security component, accessibility/print QA harness, and shared research protocol. Do not merge UkePack into those products: its music-domain transformation and teaching rules are distinct.

Current portfolio-relative rank for this audited slice:
1. UkePack — INVEST: strong coherent product, broad implementation, clear narrow wedge if validated.
2. avatar-vfo — INVEST narrowly: distinctive simulation model, deploy proof pending.
3. cf-ai-router — MAINTAIN/RESEARCH: useful infrastructure, Responses compatibility under study.
4. tick-stock-panel — SIMPLIFY/IMPROVE: useful monitoring concept, coverage truth gap.
5. lobsterpulse — SKIPPED_LOCKED this round; no new ranking claim.

## Mandatory Verification

- Total Findings: 3
- New Issues Created: 2
  - [Reese-max/UkePack #2 — P1 governance commit parser CI failure](https://github.com/Reese-max/UkePack/issues/2)
  - [Reese-max/UkePack #3 — Research: privacy-minimal workshop pack-set workflow](https://github.com/Reese-max/UkePack/issues/3)
- Updated Existing Issues: [Reese-max/UkePack #1](https://github.com/Reese-max/UkePack/issues/1)
- Reopened Issues: 0
- Research Issues: [Reese-max/UkePack #3](https://github.com/Reese-max/UkePack/issues/3)
- Duplicate Avoided: 3
- Issue Write Blocked: 0
- SKIPPED_LOCKED: Reese-max/lobsterpulse #3 / repository audit write, because branch github-3-enable-codex-hooks remains
- Rejected Findings: 10, with explicit reasons above
- Verified Fixed Issues: 0
- Priority distribution: P0 1 / P1 1 / P2 0 / P3 0 / STRATEGIC 1
- Highest Priority: UkePack #1 (P0 lineage, PARTIALLY FIXED / NEEDS_RUNTIME_VERIFICATION), followed by #2 (P1)
- Mapping completeness: 3/3 Quality-Gate findings mapped to NEW, UPDATED, or RESEARCH
