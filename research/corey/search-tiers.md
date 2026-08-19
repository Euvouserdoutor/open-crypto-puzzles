# Corey Phillips puzzle: Phase 8 tiered search strategy

## Scope and gate

This phase formalizes the exact, non-overlapping priority tiers derived in Phase 7. It does **not** call the oracle, derive keys, compare candidates with the published target, perform brute force, or authorize a real search.

The current finite model contains **59,656 exact unique candidate identities** under candidate configuration fingerprint:

```text
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52
```

The tier strategy defined here has strategy fingerprint:

```text
10940a5429829adfaa6095e44103c628f8fcc046b14c2ca4125925f66b7818bf
```

The true BIP39 passphrase domain remains unbounded because the author published no verified restriction on length, language, grammar, alphabet, source, or word count. Exhausting the finite tiers below would exhaust only the explicitly modeled R001–R006 candidate universe, **not the puzzle itself**.

## Inputs and source of truth

This strategy is based on:

- `research/corey/candidate-model.md`
- `research/corey/candidate-generation-report.md`
- `research/corey/search-space-reduction.md`
- `research/corey/solver-spec.md`
- `research/corey/oracle-validation.md`
- `tools/corey_candidates.py`

Phase 7 established:

- raw emissions: **73,492**;
- exact unique identities after safe deduplication: **59,656**;
- `SAFE_UNIQUE_N = 59,656`;
- `STRONG_N = 59,656` because there is no Class B content constraint;
- no historical candidate identity can currently be subtracted safely;
- Unicode has one verified branch: `STANDARD_BIP39_NFKD`;
- the current candidate universe can be partitioned exactly by set difference.

## Strategy principles

1. **No candidate identity appears in more than one tier.**
2. **Tier order changes priority, not coverage.** Lower-priority identities remain recoverable.
3. **No heuristic is promoted to a permanent filter.**
4. **Ordering is deterministic.** Same candidate configuration and tier strategy must produce the same identity order.
5. **Only exact candidate identity is used for deduplication.** No approximate filter may define coverage.
6. **Historical attempt aggregates are not subtracted.** The historical 1,155,064,682 attempts do not prove 1,155,064,682 unique identities.
7. **Real target evaluation remains disabled in this phase.**

## Candidate universe

Let:

```text
U = exact unique identity set emitted by enabled R001–R006
|U| = 59,656
```

Candidate identity remains:

```text
SHA256(NFKD(raw_candidate).encode("utf-8"))
```

The enabled hypotheses are:

| Hypothesis | Description | Raw | Unique internally | Confidence |
|---|---|---:|---:|---|
| H001 | Exact configured terms/phrases | 16 | 16 | WEAK |
| H002 | Simple case variants | 36 | 36 | WEAK |
| H003 | Two-token thematic expressions | 864 | 864 | WEAK |
| H004 | Three tokens, one whole-expression style | 10,368 | 10,368 | WEAK |
| H005 | Three tokens, independent boundary operations | 62,208 | 58,752 | SPECULATIVE |

Dominance and overlap established in Phase 7:

```text
R001 ⊂ R003
R005 ⊂ R006
H004 ⊂ H005
|H001 ∩ H002| = 12
```

## Formal tier definitions

### Tier 1 — Exact configured literals

Set:

```text
T1 = H001
```

Sources:

```text
R001 + R002
```

Count:

```text
|T1| = 16
```

Cumulative coverage:

```text
16 / 59,656 = 0.0268%
```

Rationale:

These candidates have the shortest provenance path from primary puzzle material to candidate construction. The source words and phrases are real, but the inference that any one was reused as the passphrase remains weak. This tier receives highest priority because it is tiny and direct, **not** because it is strongly evidenced as the secret.

Ordering:

- first-occurrence unique order from R001;
- then first-occurrence unique order from R002;
- preserve configured source ordering;
- deduplicate by candidate identity.

Tier 1 must not expand punctuation, arbitrary capitalization, numbers, synonyms, or unrelated dictionaries.

### Tier 2 — New case variants

Set:

```text
T2 = H002 \ H001
```

Source:

```text
R003
```

Count:

```text
|T2| = 24
```

Cumulative coverage:

```text
|T1 ∪ T2| = 40
40 / 59,656 = 0.0671%
```

Rationale:

R003 emits 36 candidates, but 12 lowercase forms already occur in H001. Only 24 identities add new coverage. Case is cryptographically significant and cannot be normalized away. There is no author clue supporting arbitrary mixed-case permutations, so this tier is limited to the explicit R003 model.

Ordering:

- first-occurrence unique order from R003;
- skip every identity already present in T1;
- preserve source-token order and configured case-style order.

### Tier 3 — Two-token thematic expressions

Set:

```text
T3 = H003 \ (H001 ∪ H002)
```

Source:

```text
R004
```

Count:

```text
|T3| = 864
```

Cumulative coverage:

```text
|T1 ∪ T2 ∪ T3| = 904
904 / 59,656 = 1.5153%
```

Rationale:

The historical research describes a two-token/six-style model, but the exact historical corpus is unavailable. The current R004 model is therefore a reproducible modern hypothesis, not a reconstruction of historical coverage. It is prioritized ahead of triples because it is combinatorially smaller and conceptually simpler.

Ordering:

- R004 deterministic nested-loop order;
- source token position left-to-right;
- second token position left-to-right;
- style order: `concat`, `space`, `underscore`, `hyphen`, `camel`, `pascal`;
- skip identities present in T1 or T2.

### Tier 4 — Three-token whole-expression styles

Set:

```text
T4 = H004 \ (H001 ∪ H002 ∪ H003)
```

Source:

```text
R005
```

Count:

```text
|T4| = 10,368
```

Cumulative coverage:

```text
|T1 ∪ T2 ∪ T3 ∪ T4| = 11,272
11,272 / 59,656 = 18.8950%
```

Rationale:

The three-token concept originates from an open research lead rather than a direct author clue. R005 applies one style to the whole expression, making it the narrower of the two three-token models. It precedes the independent-boundary interpretation because it has lower combinatorial complexity and fewer transformation degrees of freedom.

Ordering:

- R005 deterministic nested-loop order;
- token coordinates left-to-right;
- whole-expression style order fixed as in the candidate model;
- skip all identities already present in T1–T3.

### Tier 5 — Independent-boundary reserve

Set:

```text
T5 = H005 \ (H001 ∪ H002 ∪ H003 ∪ H004)
```

Source:

```text
R006
```

Count:

```text
|T5| = 48,384
```

Cumulative coverage:

```text
|T1 ∪ T2 ∪ T3 ∪ T4 ∪ T5| = 59,656
59,656 / 59,656 = 100% of the current finite model
```

Rationale:

R006 is the broadest enabled finite hypothesis and contributes **81.1050%** of the entire current unique model. It independently selects operations at both phrase boundaries. That interpretation is speculative and therefore remains reserve rather than early priority.

Ordering:

- R006 deterministic nested-loop order;
- token coordinates left-to-right;
- first boundary operation in configured style order;
- second boundary operation in configured style order;
- first-occurrence deduplication;
- skip every identity already assigned to T1–T4.

## Exact partition proof

The tier counts are:

```text
T1       16
T2       24
T3      864
T4   10,368
T5   48,384
     ------
     59,656
```

Therefore:

```text
T1 ∪ T2 ∪ T3 ∪ T4 ∪ T5 = U
```

and by construction:

```text
Ti ∩ Tj = ∅ for every i != j
```

No enabled R001–R006 identity is intentionally discarded.

## Tier summary

| Tier | Set expression | New unique | Cumulative | Share of U | Evidence status | Role |
|---|---|---:|---:|---:|---|---|
| 1 | H001 | 16 | 16 | 0.0268% | WEAK | Highest-priority direct literals |
| 2 | H002 \ H001 | 24 | 40 | 0.0402% new | WEAK | Case-only expansion |
| 3 | H003 \ prior | 864 | 904 | 1.4483% new | WEAK | Two-token region |
| 4 | H004 \ prior | 10,368 | 11,272 | 17.3790% new | WEAK | Whole-style triples |
| 5 | H005 \ prior | 48,384 | 59,656 | 81.1050% new | SPECULATIVE | Independent-boundary reserve |

## Information value

No empirical success probability can be honestly assigned to these tiers from the available evidence. Therefore this strategy does **not** manufacture numerical probabilities.

Qualitative information value is:

| Tier | Cost in candidate identities | Directness | Information value if exhausted |
|---|---:|---|---|
| 1 | 16 | Highest within model | High per candidate; rejects literal reuse hypothesis |
| 2 | 24 | High | High per candidate; rejects configured simple-case extension |
| 3 | 864 | Moderate | Moderate; tests bounded two-token model |
| 4 | 10,368 | Low/moderate | Moderate; tests whole-style triple lead |
| 5 | 48,384 | Lowest | Low per candidate but completes current finite model |

An exhausted tier falsifies only its explicitly defined candidate region. It does not prove broader linguistic claims.

## Search workload accounting

Cryptographic performance has not yet been benchmarked for the production search engine. Therefore Phase 8 records workload in **candidate identities**, not seconds.

| Tier | Candidate workload | Cumulative workload |
|---|---:|---:|
| 1 | 16 | 16 |
| 2 | 24 | 40 |
| 3 | 864 | 904 |
| 4 | 10,368 | 11,272 |
| 5 | 48,384 | 59,656 |

Runtime estimates must wait for later synthetic benchmark phases. No candidate/sec assumption belongs in this document.

## Historical regions not promoted to executable tiers

The following historical hypotheses remain unavailable because the exact source corpora and historical transformation semantics are missing:

| Hypothesis | Reported raw formula | Current status |
|---|---:|---|
| H100 | 7,350 | UNAVAILABLE |
| H101 | 257,250 | UNAVAILABLE |
| H102 | 1,543,500 | UNAVAILABLE |
| H103 | 7,558,272 | UNAVAILABLE |
| H104 | 45,349,632 | UNAVAILABLE |

These spaces must **not** be merged into T1–T5, and their aggregate historical attempt counts must not be treated as exact unique coverage.

Recovery of the original 35-token or 108-token corpora would define a **new candidate configuration** with a new configuration fingerprint and require candidate-space reconciliation before inclusion in any search tier.

## Historical attempt policy

Historical total:

```text
1,155,064,682 attempts
```

Historically proven unique subtractable coverage:

```text
0
```

Policy:

- do not subtract aggregate attempts;
- do not mark current identities as previously tested without exact normalized identity evidence;
- if historical manifests/fingerprints are recovered, intersect exact candidate IDs with the current tier universe;
- preserve provenance and distinguish historical reruns from unique identities.

## Unicode policy

Only one verified candidate identity branch is active:

```text
STANDARD_BIP39_NFKD
```

No redundant legacy raw-Unicode branch is included. If future evidence demonstrates a materially different historical implementation relevant to candidate identity, candidate configuration semantics must change and the fingerprint must be regenerated before any coverage claim.

## Deterministic tier assignment contract

For each unique candidate identity in first-occurrence generator order:

```text
if id ∈ H001:
    tier = 1
elif id ∈ H002:
    tier = 2
elif id ∈ H003:
    tier = 3
elif id ∈ H004:
    tier = 4
elif id ∈ H005:
    tier = 5
else:
    ERROR
```

This precedence is equivalent to the explicit set-difference definitions above because all enabled identities are members of H001–H005.

Tier assignment must be reproducible from the candidate configuration and must not depend on search results.

## Checkpoint implications for the future solver

Phase 8 does not implement checkpoints, but the future solver must preserve at least:

```text
candidate_config_fingerprint
tier_strategy_fingerprint
tier
raw/unique stream position as applicable
last committed candidate identity or deterministic ordinal
tested unique candidate count
```

A resume operation must reject a checkpoint if either the candidate configuration fingerprint or tier strategy fingerprint differs.

Changing any of the following requires a new tier-strategy fingerprint:

- tier membership;
- tier precedence;
- set-difference logic;
- source rules included in a tier;
- ordering semantics;
- candidate configuration fingerprint.

## Coverage semantics

Future status meanings must be precise:

### `TIER_EXHAUSTED`

Every exact unique identity assigned to that tier under the recorded fingerprints was evaluated once successfully or otherwise accounted for under an explicit recoverable error policy.

### `MODEL_EXHAUSTED`

All 59,656 identities in T1–T5 were covered under the recorded finite model.

### `PUZZLE_EXHAUSTED`

**Not a valid status.** The true passphrase space is not bounded by available evidence.

## Fail-closed conditions

Tier planning or later execution must stop on:

- candidate configuration fingerprint mismatch;
- tier strategy fingerprint mismatch;
- identity count mismatch;
- set-overlap detected between executable tiers;
- missing candidate provenance;
- Unicode normalization semantics change;
- candidate generator nondeterminism;
- unexplained count divergence from `59,656`;
- recovery of historical source data that changes the intended candidate universe without a new configuration review.

## Pre-implementation invariants

Before a future search engine can consume this strategy, it must be able to verify without calling the real target:

1. T1 count = 16.
2. T2 count = 24.
3. T3 count = 864.
4. T4 count = 10,368.
5. T5 count = 48,384.
6. Total = 59,656.
7. Pairwise tier intersections are empty.
8. Tier union equals current exact unique candidate universe.
9. Candidate configuration fingerprint matches `41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52`.
10. Tier strategy fingerprint matches `10940a5429829adfaa6095e44103c628f8fcc046b14c2ca4125925f66b7818bf` when calculated from the documented canonical strategy object.

## Safety boundary

This strategy applies exclusively to the intentionally published Corey Phillips puzzle. It does not authorize:

- unrelated wallet scanning;
- arbitrary address enumeration;
- transaction creation;
- automatic fund movement;
- candidate search outside the documented public puzzle target;
- automatic progression from one tier to the next.

No tier should automatically trigger the next tier after completion.

## Phase 8 gate

```text
Phase 8: COMPLETE

Tier strategy: COMPLETE
Candidate configuration fingerprint:
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52

Tier strategy fingerprint:
10940a5429829adfaa6095e44103c628f8fcc046b14c2ca4125925f66b7818bf

SAFE unique universe: 59,656

Tier 1: 16
Tier 2: 24
Tier 3: 864
Tier 4: 10,368
Tier 5 / reserve: 48,384

Cumulative total: 59,656
Pairwise overlap: 0 by set-difference construction
Finite-model coverage preserved: YES
Historical aggregate subtraction: NO
Historical unavailable regions included: NO
Unicode branch: STANDARD_BIP39_NFKD

Real oracle calls: 0
Real puzzle target comparisons: 0
Real candidate search: NO

Ready for Phase 9 search-engine implementation: GO
Real search authorization: NO-GO
```

## Hard stop

Phase 8 ends here.

Do not:

- call the real oracle on T1;
- test the 16 Tier 1 identities;
- implement a hidden automatic search;
- launch multiprocessing;
- benchmark real candidate-to-target throughput;
- use GPU acceleration;
- start Tier 2 after Tier 1;
- import unavailable historical corpora speculatively;
- perform a transaction.

The next permitted activity is **search-engine implementation and synthetic validation only**, using this tier strategy as a contract.