# Corey Phillips puzzle: Phase 7 search-space reduction

## Scope and decision boundary

This report reduces and prioritizes the deterministic Phase 6 candidate model.
It does not derive keys, call an oracle, compare a candidate with the target or
perform a search. Every non-safe reduction remains reversible.

The central result is deliberately conservative: exact deduplication safely
reduces 73,492 emissions to 59,656 identities. No non-protocol clue is strong
enough to permanently remove another identity. The 59,656 identities can,
however, be partitioned exactly into non-overlapping priority regions.

## Reproduced Phase 6 baseline

The Phase 6 stream was regenerated and recounted without cryptographic
derivation.

| Metric | Reproduced value | Phase 6 value | Agreement |
|---|---:|---:|---|
| Raw candidates | 73,492 | 73,492 | Yes |
| Protocol-normalized emissions | 73,492 | 73,492 | Yes |
| Exact unique identities | 59,656 | 59,656 | Yes |
| Evidence-backed unique | 16 | 16 | Yes |
| Hypothesis-backed unique | 59,652 | 59,652 | Yes |
| Smallest enabled hypothesis | H001: 16 | H001: 16 | Yes |
| Largest enabled hypothesis | H005: 62,208 raw; 58,752 unique | Same | Yes |

The evidence and hypothesis sets overlap by 12 identities; their unique totals
must not be added.

## Configuration consistency

| Field | Value |
|---|---|
| Generator version | `1.0.0` |
| Source commit containing the Phase 6 generator | `449df79c8c5d186f02e0ab7d9129e068aed4cd07` |
| Candidate configuration fingerprint | `41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52` |
| Normalization | NFKD then UTF-8 |
| Unicode mode | `STANDARD_BIP39_NFKD` |
| Unicode database used for counts | 15.0.0 |
| Enabled hypotheses | H001–H005 |
| Enabled rules | R001–R006 |

Phase 7 does not change generator semantics, so the fingerprint remains
unchanged.

## Evidence Map

| Evidence ID | Description | Primary source | Reliability | Relevant hypotheses |
|---|---|---|---|---|
| E001 | Author says the kitten image was combined with a BIP39 passphrase | `clues/author-posts.md` | PRIMARY | H001–H005 only as candidate inferences |
| E002 | Original mechanism fixes image, mnemonic, BIP84 path, network and address type; passphrase is the primary unknown | Original source audit in `oracle-validation.md` | PRIMARY | Protocol, not vocabulary |
| E003 | Exact public JPEG visibly contains five kittens | `clues/kitten.jpeg` | PRIMARY | H001 weakly; numeric use speculative |
| E004 | Author says the construction was not meant to be solved | `clues/author-posts.md` | PRIMARY | Weakens human-password assumptions |
| E005 | Article/tool contain kitten, image, mnemonic, passphrase and Bitcoin terms plus short phrases | Author post and tool title | PRIMARY | H001–H005 |
| E006 | No reviewed primary source states length, language, word count, alphabet, case, punctuation or source | Primary-material audit | STRONG | Prevents unsupported exclusions |
| E007 | Author's 2019 bundle applies NFKD to both BIP39 inputs | `unicode-validation.md` | PRIMARY | Safe identity rule |
| E008 | R001–R006 reproduce exact counts and overlaps | Generator and Phase 6 report | STRONG | H001–H005 |
| E009 | Historical ledger totals 1,155,064,682 attempts, not proven unique identities | `analysis/tested.md`, `coverage.csv` | MODERATE | Historical coverage only |
| E010 | Historical manifests, normalized fingerprints and run boundaries are absent | Repository audit | STRONG | H100–H104 unavailable |
| E011 | Historical 35-token/two-word/six-style region is reported; corpus absent | `analysis/tested.md` | MODERATE | H100–H102 |
| E012 | Historical 108-token author corpus is reported; corpus/rules absent | `analysis/tested.md` | MODERATE | H103–H104 |
| E013 | Three-word extension is a research lead, not an author clue | `analysis/leads.md` | WEAK | H004–H005 |
| E014 | Related audio puzzle reuses 24-word BIP84 structure but reveals no passphrase pattern | README/tested ledger | MODERATE | Mechanism only |
| E015 | Historical local audit reports no hidden JPEG payload; raw audit outputs absent | `analysis/tested.md` | MODERATE | Negative clue channel |
| E016 | S001/S002 are new Phase 6 sources, not historical corpora; S002 is lowercase and unpunctuated by definition | Candidate model/source | STRONG | H001–H005 |

The most important distinction is E005 versus the hypothesis it motivates.
The words are unquestionably present, but there is only weak evidence that the
author reused them as the secret.

## Constraint Registry

| ID | Class | Constraint | Evidence | Confidence | False-negative risk | Use |
|---|---|---|---|---|---|---|
| C001 | A SAFE | Identity is SHA256 of NFKD UTF-8 | E002, E007 | PROTOCOL | NONE | Permanent |
| C002 | A SAFE | Exact global identity deduplication | E008 | CONFIRMED | NONE | Permanent |
| C003 | A SAFE | Schedule R003 only-new after R001 | E008 | CONFIRMED | NONE | Permanent |
| C004 | A SAFE | Schedule R006 only-new after R005 and remove internal repeats | E008 | CONFIRMED | NONE | Permanent |
| C005 | A SAFE | Keep only verified NFKD behavior; no redundant raw-compat branch | E007 | CONFIRMED | NONE | Permanent |
| C006 | A SAFE | Invalid generator/configuration state is an error | E002, E008 | PROTOCOL | NONE | Permanent |
| C007 | A SAFE | Empty passphrase is known calibration and absent from R001–R006 | E002 | CONFIRMED | NONE | Permanent |
| C008 | C HYPOTHESIS | Exact configured literals first | E001, E005, E016 | WEAK | HIGH if exclusion | Tier only |
| C009 | C HYPOTHESIS | Casing-only new identities second | E005, E016 | WEAK | HIGH if exclusion | Tier only |
| C010 | C HYPOTHESIS | Two-token region next | E005, E011, E016 | WEAK | HIGH if exclusion | Tier only |
| C011 | C HYPOTHESIS | Whole-style triples below shorter regions | E005, E013, E016 | WEAK | HIGH if exclusion | Tier only |
| C012 | C HYPOTHESIS | Independent-boundary-only identities in reserve | E013, E016 | SPECULATIVE | HIGH if exclusion | Tier only |
| C013 | D DANGEROUS | ASCII-only secret | E006, E008 | SPECULATIVE | UNKNOWN | Do not use |
| C014 | D DANGEROUS | Lowercase/no-uppercase only | E006 | SPECULATIVE | HIGH | Experiment only |
| C015 | D DANGEROUS | Exactly one semantic token | E006 | SPECULATIVE | HIGH | Do not use |
| C016 | D DANGEROUS | At most three semantic tokens | E006 | SPECULATIVE | HIGH | Do not use |
| C017 | D DANGEROUS | Maximum length 16 | E006 | SPECULATIVE | HIGH | Do not use |
| C018 | D DANGEROUS | Exclude hyphen and underscore | E006 | SPECULATIVE | HIGH | Experiment only |
| C019 | D DANGEROUS | Exclude digits | E003, E006 | SPECULATIVE | HIGH | Do not use |
| C020 | D DANGEROUS | Keep only space/concatenation styles | E006, E011 | SPECULATIVE | HIGH | Experiment only |
| C021 | D DANGEROUS | Preserve publication/source chronology as token order | E006 | SPECULATIVE | HIGH | Do not use |
| C022 | D DANGEROUS | Subtract historical aggregates without identities | E009, E010 | SPECULATIVE | UNKNOWN | Do not use |

There are no Class B constraints. Direct primary evidence establishes the
mechanism but supplies no strong passphrase-content restriction.

## Protocol-level and exact-duplicate reduction

| Step | Before | After | Removed | Factor | False-negative risk |
|---|---:|---:|---:|---:|---|
| NFKD protocol normalization | 73,492 emissions | 73,492 emissions | 0 collision events | 1.000000x | NONE |
| Exact identity deduplication | 73,492 | 59,656 | 13,836 emissions | 1.231930x | NONE |
| Further safe exclusions after unique baseline | 59,656 | 59,656 | 0 identities | 1.000000x | NONE |

Duplicate decomposition:

- R006 contains 3,456 same-rule duplicate emissions.
- R001 and R003 share 12 identities.
- R005 and R006 share 10,368 identities.
- Different raw Unicode strings produce zero NFKD collisions in the current
  ASCII corpus.

`SAFE_UNIQUE_N = 59,656` exactly.

## Marginal hypothesis contribution

| Hypothesis | Raw | Unique internally | New vs previous | Overlap | Marginal share of SAFE |
|---|---:|---:|---:|---:|---:|
| H001 | 16 | 16 | 16 | 0.00% | 0.0268% |
| H002 | 36 | 36 | 24 | 33.33% | 0.0402% |
| H003 | 864 | 864 | 864 | 0.00% | 1.4483% |
| H004 | 10,368 | 10,368 | 10,368 | 0.00% | 17.3790% |
| H005 | 62,208 | 58,752 | 48,384 | 17.65% | 81.1050% |

H004 is a complete subset of H005. H001/H002 share 12 lowercase literals.
No hypothesis is deleted; later regions use set difference.

## Marginal rule contribution

| Rule | Raw | Unique within rule | Internal duplicate rate | Overlap with prior rules | Marginal unique |
|---|---:|---:|---:|---:|---:|
| R001 | 12 | 12 | 0% | 0 | 12 |
| R002 | 4 | 4 | 0% | 0 | 4 |
| R003 | 36 | 36 | 0% | 12 | 24 |
| R004 | 864 | 864 | 0% | 0 | 864 |
| R005 | 10,368 | 10,368 | 0% | 0 | 10,368 |
| R006 | 62,208 | 58,752 | 5.56% | 10,368 | 48,384 |

R006 contributes the most new identities and has the highest internal duplicate
rate. R001 and R005 have zero scheduling information once their supersets are
reached, but retain provenance and earlier priority value.

## Clue-to-candidate traceability

| Region | Rules | Evidence | Unique candidates | Confidence |
|---|---|---|---:|---|
| Configured literal terms/phrases | R001–R002 | E001, E005, E016 | 16 | WEAK as secret hypothesis |
| Case variants | R003 | E005, E016 | 36; 24 new | WEAK |
| Two-token thematic expressions | R004 | E005, E011, E016 | 864 | WEAK |
| Three-token whole styles | R005 | E005, E013, E016 | 10,368 | WEAK |
| Independent boundary styles | R006 | E013, E016 | 58,752; 48,384 new | SPECULATIVE |
| Historical 35/108-token spaces | R100–R104 | E009–E012 | UNKNOWN | Unavailable |

Provenance includes rule, hypothesis, source IDs, transformations and stable raw
index. The index permits deterministic reconstruction of token coordinates even
though the compact record does not separately store the input token tuple.

## Author-clue semantic analysis

### Vocabulary and wording

Primary wording directly supplies `kitten`, `image`, `BIP39`, `passphrase`,
`mnemonic`, Bitcoin language, the tool name `bitimage`, the author name and the
phrases about not being solved and managing to claim it. This supports a small
priority experiment, not exclusion of other vocabulary.

R002 must not be described as verbatim quotation coverage. Its four configured
values are lowercase and omit source punctuation. The author quotation includes
sentence capitalization, commas, periods and an exclamation mark. Those variants
are outside the current model.

Singular/plural is unconstrained. The prose uses singular “kitten image,” while
the image visibly contains five kittens. `satoshis` is a derived thematic token,
not an explicit passphrase hint. No synonym, pluralization or substitution rule
is justified as a safe transformation.

### Character set and capitalization

All 59,656 current identities are ASCII because S001/S002 are ASCII. That is a
generator property, not an author constraint; BIP39 accepts Unicode after NFKD.
Case and ordinary whitespace remain cryptographically significant.

| Current-model property | Unique identities |
|---|---:|
| ASCII | 59,656 |
| Non-ASCII | 0 |
| Contains uppercase | 31,416 |
| Contains no uppercase | 28,240 |
| Contains a digit | 25,022 |
| Contains no digit | 34,634 |
| Contains a space | 19,156 |
| Contains underscore | 19,152 |
| Contains hyphen | 19,152 |

R003 contributes 12 lowercase, 12 title-first and 12 uppercase values; the 12
lowercase values duplicate R001. Arbitrary mixed-case masks are neither generated
nor supported.

### Length analysis

Lengths are Unicode code points in the exact current unique stream.

| Length | Unique candidates | Confidence as a constraint |
|---|---:|---|
| 1–8 | 33 | NONE |
| 9–16 | 1,977 | NONE |
| 17–24 | 49,044 | NONE |
| 25–32 | 8,599 | NONE |
| 33–48 | 2 | NONE |
| 49+ | 1 | NONE |

These counts describe model output only. No maximum or minimum is safe.

### Word-count analysis

Using generator semantics rather than surface separators gives a disjoint exact
partition:

| Region | Unique identities | Evidence confidence |
|---|---:|---|
| One configured token, including case variants | 36 | WEAK |
| Configured multiword literal phrases | 4 | WEAK |
| Two configured tokens | 864 | WEAK |
| Three configured tokens | 58,752 | WEAK/SPECULATIVE |

“25th word” is BIP39 wallet terminology and does not imply a one-word secret.

### Separator analysis

R004 has 144 unique identities per style. R005 has 1,728 per style. Every R006
boundary coordinate emits 1,728 values, but coordinates overlap and R006 has
58,752 unique identities rather than 62,208. The six styles are concatenation,
space, underscore, hyphen, camel and Pascal.

The only support for this exact six-style family is the historical ledger and
Phase 6's explicit model. The author provides no passphrase-separator clue.
Keeping only space/concatenation coordinates plus literal/case rules would leave
3,784 identities, but C020 is dangerous and cannot be permanent.

### Punctuation and numbers

The source quotation visibly uses ordinary punctuation, including the terminal
punctuation omitted by R002. Current punctuation generation is limited to hyphen
and underscore separators; it does not add `!`, `.`, `?`, commas or apostrophes.
No evidence supports a permanent punctuation filter.

Potential numbers visible in local evidence include five kittens, 2019-07-09,
0.01 BTC, 24/“25th word,” BIP84 and 2,048 PBKDF2 iterations. They describe the
artifact or mechanism. Appending/spelling them would expand rather than reduce
the model, and no such rule is implemented.

| Potential transformation | Evidence | New unique candidates | Confidence |
|---|---|---:|---|
| Append/prepend `5` or `five` | Five kittens visible | NOT MODELED | SPECULATIVE |
| Use `2019` or publication date | Publication metadata | NOT MODELED | SPECULATIVE |
| Use `24`, `25`, `84` or `2048` | Protocol/mechanism numbers | NOT MODELED | SPECULATIVE |
| Decimal reward representations | Funding statement | NOT MODELED | SPECULATIVE |

### Ordering and chronology

The pipeline order and fixed 24-word mnemonic order are cryptographic facts, but
no evidence maps publication order to passphrase-token order. R004–R006 correctly
preserve all ordered selections with replacement. C021 would be a dangerous
linguistic filter.

### Author-specific and sibling-puzzle patterns

| Previous puzzle | Verified mechanism | Potential relevance | Confidence |
|---|---|---|---|
| 2020 Bitcoin Audio Puzzle | Encoded message leads to a 24-word BIP84 structure | Author reused modern SegWit/BIP84 mechanics | MODERATE |

The local repository contains no verified solved sibling by this author that
reveals how he chooses BIP39 passphrases. Structural similarity does not imply a
shared secret, vocabulary, capitalization or word count.

## Additional reference triage

Seven external references supplied during Phase 7 were inspected for relevance
before use:

| References | Actual subject | Relationship to Corey | Decision |
|---|---|---|---|
| [1], [2], [3], [5], [6] | A separate BLM-themed 0.2 BTC image puzzle involving seed-word extraction, runes and ordering | Different image, creator, target format and mechanism | Excluded from Corey evidence |
| [4] | The 2015 puzzle transaction whose private keys occupy deliberately bounded numeric ranges | Private-key range puzzle, not BIP39 passphrase selection | Excluded from Corey evidence |
| [7] | AlberTajuelo's research repository for the same BLM 0.2 BTC image puzzle; the original is unavailable, with its README preserved in public forks | No shared author or mechanism | Methodology only |

The BLM repository's useful transferable practice is procedural: separate visual
observations from interpretations, preserve exact spelling/typos, assign ordering
hypotheses explicitly and keep competing derivation formats as branches. Those
principles are already enforced here by E/C identifiers, literal-versus-edited
source warnings and reversible set-difference tiers.

No words, dates, addresses, rune interpretations, BIP39 positions or candidate
ideas from these unrelated puzzles were added to S001/S002. The address in
reference [6] was not queried. Consequently, the evidence registry, counts,
constraints and configuration fingerprint are unchanged.

Reference URLs:

- [1] `https://www.reddit.com/r/bitcoinpuzzles/comments/jrr7mo/is_this_puzzle_still_valid_is_this_image_correct/`
- [2] `https://www.reddit.com/user/stsh_n/comments/j79zvj/bitcoin_puzzle_2000/`
- [3] `https://www.reddit.com/r/CryptoPuzzlers/comments/mbdogq/02_btc_puzzle/`
- [4] `https://bitcointalk.org/index.php?topic=1306983.0`
- [5] `https://bitcointalk.org/index.php?topic=5404767.0`
- [7 preserved fork] `https://github.com/jmr2704/bitcoin-0.2-image-puzzle`

## Negative evidence and Historical Coverage

No current candidate identity can be marked exhausted from the historical
aggregate.

| Region | Historical evidence | Coverage confidence | Can exclude now? |
|---|---|---|---|
| Generic wordlists/rules | Counts and witness claims only | Probably processed; unique set unknown | No |
| 108-word Corey corpus | 23,735,781 attempts; corpus absent | Probably processed; identities unknown | No |
| In-joke phrases | 2,808,334 attempts; source absent | Probably processed; identities unknown | No |
| 35-word two-token region | 7,350 attempts; corpus absent | Raw formula plausible | No |
| Quotes/BIP39 words | 29,201 attempts; manifests absent | Unknown exact coverage | No |
| Audio variants | 32 attempts; values not fully recorded | Partial description only | No |
| Alternate paths | 432 derivations, not passphrase identities | Not primary-space coverage | No |
| Independent cross-check | 7,454 overlapping attempts | Explicitly non-unique | No |

Historically proven unique coverage usable for subtraction is **0**. Historical
uncertain coverage is **1,155,064,682 attempts**, with unique count unknown.

## Information-gain experiments

### X001 — Recover historical manifests

- Question: Which normalized identities were actually processed?
- Required inputs: exact 35/108-token corpora, rule files, run manifests or sorted
  candidate fingerprints.
- Cost: data recovery and deterministic reconciliation; no oracle.
- Expected information gain: very high.
- Outcomes: exact intersection becomes known, or historical coverage remains
  unusable.
- Search-space effect: potentially removes proven repeats with zero false-negative
  risk.

### X002 — Ask for one author constraint

- Question: Is the passphrase one word/phrase, language, approximate length, theme
  or public source?
- Required inputs: a human-authored message to the puzzle creator.
- Cost: minimal compute; requires human contact.
- Expected information gain: maximal because the global domain is unbounded.
- Outcomes: recalculate bounded regions or retain current uncertainty.
- Search-space effect: potentially orders or removes whole model branches, but only
  after an authenticated, unambiguous reply.

### X003 — Audit primary text fidelity

- Question: Which exact capitalization and punctuation variants occur in the
  pinned article/tool source?
- Required inputs: archived primary HTML and pinned tool commit.
- Cost: small deterministic text audit.
- Expected information gain: moderate for H001/S002 quality.
- Outcomes: replace edited phrase values with a versioned verbatim source or retain
  them as researcher-defined hypotheses.
- Search-space effect: small but improves provenance.

### X004 — Reproduce the image-channel negative

- Question: Can clean metadata/container findings be reproduced from the committed
  JPEG with retained outputs?
- Required inputs: current JPEG and bounded metadata/container inspection.
- Cost: small; no candidate generation.
- Expected information gain: low to moderate.
- Outcomes: certify or downgrade E015.
- Search-space effect: affects clue-channel confidence, not an exact candidate count.

### X005 — Establish whether the five-kitten count was intentional

- Question: Is the visible count referenced by the original caption/source, or is it
  incidental stock imagery?
- Required inputs: primary caption and artifact provenance.
- Cost: small source audit.
- Expected information gain: low.
- Outcomes: numeric transformations remain speculative or gain direct evidence.
- Search-space effect: prevents arbitrary numeric expansion; no current exclusion.

## Reduction Impact Table

Safe constraints are cumulative only where stated. Dominance rows decompose the
same global deduplication and must not be counted twice.

| Constraint | Before | After | Removed | Factor | Risk |
|---|---:|---:|---:|---:|---|
| C001 NFKD | 73,492 | 73,492 | 0 | 1.0000x | NONE |
| C002 exact global dedup | 73,492 | 59,656 | 13,836 | 1.2319x | NONE |
| C003 R001/R003 dominance | 48 emissions | 36 identities | 12 | 1.3333x | NONE |
| C004 R005/R006/internal dominance | 72,576 emissions | 58,752 identities | 13,824 | 1.2353x | NONE |
| C014 no uppercase | 59,656 | 28,240 | 31,416 | 2.1125x | HIGH |
| C015 one semantic token | 59,656 | 36 | 59,620 | 1,657.1x | HIGH |
| C017 length <=16 | 59,656 | 2,010 | 57,646 | 29.6796x | HIGH |
| C018 no hyphen/underscore | 59,656 | 24,808 | 34,848 | 2.4047x | HIGH |
| C019 no digits | 59,656 | 34,634 | 25,022 | 1.7225x | HIGH |
| C020 space/concat coordinates | 59,656 | 3,784 | 55,872 | 15.7653x | HIGH |
| C022 historical aggregate subtraction | 59,656 | UNKNOWN | UNKNOWN | INVALID | UNKNOWN |

## Cumulative safe and strong-evidence spaces

```text
RAW EMISSIONS                         73,492
  minus exact duplicate emissions    13,836
SAFE / EXACT UNIQUE                  59,656
  minus Class B strong exclusions         0
STRONG_N                             59,656
```

There is no Class B content constraint. Therefore `STRONG_N = 59,656` exactly,
and the strong-evidence reduction factor from SAFE is 1.000000x. The 16-literal
region is the most direct candidate region, but its link to the secret is WEAK;
calling it `STRONG_N` would overstate the evidence.

## Hypothesis-prioritized space and set differences

| Priority | Set expression | New unique | Cumulative | Treatment |
|---|---|---:|---:|---|
| HIGH / preliminary Tier 1 | H001 | 16 | 16 | Exact configured literals |
| HIGH / preliminary Tier 2 | H002 minus H001 | 24 | 40 | New case variants only |
| MEDIUM / preliminary Tier 3 | H003 minus (H001 union H002) | 864 | 904 | Two-token region |
| LOW / preliminary Tier 4 | H004 minus prior | 10,368 | 11,272 | Whole-style triples |
| RESERVE | H005 minus prior | 48,384 | 59,656 | Independent-boundary-only identities |

This is an exact partition. Preliminary tiers are proposals for Phase 8, not
executable search authorization.

## Risk-weighted reduction

| Constraint | Compute reduction | Evidence strength | False-negative risk | Recommended use |
|---|---:|---|---|---|
| Exact identity dedup | 18.83% emissions | PROTOCOL/CONFIRMED | NONE | PERMANENT FILTER |
| Literal-first ordering | No loss; first 16 | WEAK candidate inference | NONE when tiered | TIER PRIORITY |
| Whole-style before independent boundaries | First 11,272 cumulative | WEAK | NONE when reserve retained | TIER PRIORITY |
| One-token-only | 99.94% | None | HIGH | DO NOT USE |
| Length <=16 | 96.63% | None | HIGH | DO NOT USE |
| Historical aggregate subtraction | Unknown, potentially large | Incomplete ledger | UNKNOWN | DO NOT USE |

## Search-space waterfall

```text
RAW                                       73,492
  exact duplicate/NFKD identity removal  -13,836
SAFE UNIQUE                               59,656
  Class B strong filters                       0
STRONG                                    59,656

Priority partition of STRONG/SAFE:
  Tier 1                                      16
  Tier 2 only-new                             24
  Tier 3 only-new                            864
  Tier 4 only-new                         10,368
  Reserve only-new                        48,384
                                           ------
                                           59,656
```

## Tempting but Unsafe Reductions

- Treating “25th word” as exactly one dictionary word would retain only 36
  current semantic one-token identities and discard 59,620.
- Restricting to length 16 would retain 2,010 but has no author support.
- Lowercase-only would discard 31,416 even though BIP39 case is significant.
- Space/concatenation-only would retain 3,784, but the historical model itself
  records six styles.
- Assuming ASCII is especially dangerous outside the current model: it saves
  nothing inside R001–R006 and silently discards the protocol's Unicode domain.
- Subtracting the 1.155-billion attempt total could discard untested identities
  because candidate manifests and normalization history are missing.

## Assumption sensitivity

| Assumption | If true | If false | Ratio/impact |
|---|---:|---:|---:|
| Independent boundary styles unnecessary | 11,272 enabled identities suffice | 59,656 retained | 5.2923x |
| Secret is one configured semantic token | 36 | 59,656 | 1,657.1x |
| Maximum length is 16 | 2,010 | 59,656 | 29.6796x |
| Only space/concat coordinates matter | 3,784 | 59,656 | 15.7653x |
| No uppercase | 28,240 | 59,656 | 2.1125x |
| No digits | 34,634 | 59,656 | 1.7225x |
| Historical identities recoverable | Exact prior intersection becomes subtractable | No safe historical subtraction | UNKNOWN |

The largest uncertainty overall is not a row in the finite model: the author
published no bound on the passphrase domain, so the true evidence-constrained
space remains unbounded. Within R001–R006, the independent-boundary assumption
has the largest branch impact, contributing 48,384 new identities.

## Search-space branches and dominance

Unicode has one verified branch: `STANDARD_BIP39_NFKD`. No legacy branch is
needed. Candidate uncertainty is preserved as nested set-difference branches.

Confirmed dominance:

```text
R001 is a strict subset of R003
R005 is a strict subset of R006
H004 is a strict subset of H005
```

H001 is not a subset of H002 because its four phrase values are not in R003;
their intersection is 12. These relations explain all non-zero cross-rule and
cross-hypothesis overlap.

## Preliminary Phase 8 tier proposal

- Tier 1: H001, 16 identities.
- Tier 2: H002 only-new, 24 identities.
- Tier 3: H003 only-new, 864 identities.
- Tier 4: H004 only-new, 10,368 identities.
- Reserve: H005 only-new, 48,384 identities.
- Unavailable reserve: H100–H104, exact unique sizes unknown until corpora and
  historical style semantics are recovered.

This structure ranks clue directness and preserves every enabled identity. It
does not finalize a search plan or permit candidate evaluation.

## Validation and blockers

The Phase 6 configuration and counts were reproduced exactly. Set inclusion,
set intersection and set-difference counts were calculated from full SHA256
identity sets under the unchanged fingerprint. Existing generator tests and
self-test remain the applicable logic checks; no reduction code or solver code
was added.

Remaining blockers:

- true passphrase length, language, grammar, source and alphabet remain unknown;
- historical 35/108-token corpora and exact rule semantics are missing;
- historical identities cannot be subtracted;
- S002 is not a verbatim punctuation/case corpus;
- no strong content clue exists, so all finite tiers remain heuristic.

Phase 8 tier-strategy design is ready because safe filters, heuristic tiers,
overlaps, set differences and Unicode behavior are explicit and reproducible.
This does not authorize Tier 1 execution.
