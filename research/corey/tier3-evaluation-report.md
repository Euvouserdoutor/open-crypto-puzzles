# Corey Phillips puzzle: Tier 3 evaluation report

## Scope

This report records the separately authorized Tier 3 experiment against the
intentionally published Corey Phillips reward puzzle.

Only the 864 new Tier 3 identities were evaluated. Exact set-difference tiering
excluded all Tier 1 and Tier 2 identities. The solver did not start Tier 4,
accept an arbitrary target, access a network, create a transaction, or move
funds.

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
tier = 3
maximum candidates = 864
processes = 1
automatic next tier = disabled
```

Tier 3 is the deterministic R004 two-token region under the six configured
whole-expression styles.

## Result

```text
Status: TIER_EXHAUSTED
Tier: 3
Tier size: 864
Evaluated successfully: 864
Oracle errors: 0
Matches: 0
Next ordinal: 864
Checkpoint complete: true
Tier 4 started: no
```

No match result file was created.

Final redacted checkpoint evidence:

```text
last_candidate_id:
e5b335cc01ec80095ff1e449fc5fecf6441900c732d641b7ad2f3b60b9141d85

progress_digest:
268ecd92b6369b6a37407da502e0750605ed4a9224c96e6cd4dca268f091c197
```

Deterministic replay of all 864 checkpointed identities passed. The checkpoint
contained no raw or normalized passphrase.

Observed end-to-end wall time was approximately 2.8 minutes, including the full
partition and two-oracle preflight. This is not a controlled pure-oracle
throughput benchmark.

## Cumulative finite-model coverage

```text
Tier 1: 16/16, no match
Tier 2: 24/24, no match
Tier 3: 864/864, no match
Cumulative exact unique identities evaluated: 904
Cumulative share of current 59,656-identity model: approximately 1.5153%
```

This coverage statement applies only to the current finite R001-R006 model. It
does not bound the real BIP39 passphrase domain and does not incorporate the
historical aggregate attempt count.

## Gate after Tier 3

```text
Tier 1: EXHAUSTED — no match
Tier 2: EXHAUSTED — no match
Tier 3: EXHAUSTED — no match
Tier 4: NOT STARTED — 10,368 identities
Tier 5: NOT STARTED

Automatic progression: DISABLED
Tier 4 authorization: NO-GO
Transactions or fund movement: NO-GO
```

Tier 4 requires a separate explicit authorization and a new checkpoint.
