# Corey Phillips puzzle: Tier 2 evaluation report

## Scope

This report records the separately authorized Tier 2 experiment against the
intentionally published Corey Phillips reward puzzle.

Only the 24 new Tier 2 candidate identities were evaluated. Tier 1 identities
were excluded by exact set difference and were not rerun. The solver did not
start Tier 3, accept an arbitrary target, access a network, create a
transaction, or move funds.

## Reproducibility contracts

```text
Candidate configuration fingerprint:
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52

Canonical tier strategy fingerprint:
7f2685ceaeae227a4b85be8431c4c53546b26aa62938f6816282080a7211d61a

Unicode mode:
STANDARD_BIP39_NFKD

Checkpoint schema:
corey-phase10-checkpoint-v1
```

## Preconditions

Immediately before evaluation, the solver again passed:

- canonical strategy and candidate configuration fingerprint recomputation;
- exact tier count, disjointness, ordering, and union validation;
- Python oracle self-test;
- independent JavaScript oracle validation;
- synthetic Unicode end-to-end address agreement;
- synthetic NFKD digest agreement;
- explicit public-puzzle authorization gate.

## Execution boundary

```text
mode = EVALUATE
tier = 2
maximum candidates = 24
processes = 1
automatic next tier = disabled
```

## Result

```text
Status: TIER_EXHAUSTED
Tier: 2
Tier size: 24
Evaluated successfully: 24
Oracle errors: 0
Matches: 0
Next ordinal: 24
Checkpoint complete: true
Tier 3 started: no
```

No match result file was created.

Final redacted checkpoint evidence:

```text
last_candidate_id:
c96559c628961866ae6d7a49f2e5079efe4f561d0227611bb18534d44b33f005

progress_digest:
0e2de0edf315aab67905e4d57608700050a700d2f4d2d05fe27c6e80a16f1ea7
```

Deterministic replay of all 24 checkpointed identities passed. The checkpoint
contained no raw or normalized passphrase.

Observed wall time was approximately 8.2 seconds, including the full partition
and two-oracle preflight. This is not a pure candidate-per-second benchmark.

## Cumulative finite-model coverage

```text
Tier 1: 16/16, no match
Tier 2: 24/24, no match
Cumulative exact unique identities evaluated: 40
Cumulative share of current 59,656-identity model: approximately 0.0671%
```

This cumulative value is exact only for the current finite R001-R006 model. It
does not bound the real BIP39 passphrase domain and does not incorporate the
historical aggregate attempt count.

## Gate after Tier 2

```text
Tier 1: EXHAUSTED — no match
Tier 2: EXHAUSTED — no match
Tier 3: NOT STARTED — 864 identities
Tier 4: NOT STARTED
Tier 5: NOT STARTED

Automatic progression: DISABLED
Tier 3 authorization: NO-GO
Transactions or fund movement: NO-GO
```

Tier 3 requires a separate explicit authorization and a new checkpoint.
