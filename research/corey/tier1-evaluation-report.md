# Corey Phillips puzzle: Tier 1 evaluation report

## Scope

This report records the first explicitly authorized real-candidate experiment
against the intentionally published Corey Phillips reward puzzle.

Only Tier 1 was evaluated. The solver did not start Tier 2, accept an arbitrary
target, access a network, create a transaction, or move funds.

## Reproducibility contracts

Candidate configuration fingerprint:

```text
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52
```

Canonical tier strategy fingerprint:

```text
7f2685ceaeae227a4b85be8431c4c53546b26aa62938f6816282080a7211d61a
```

Unicode mode:

```text
STANDARD_BIP39_NFKD
```

Checkpoint schema:

```text
corey-phase10-checkpoint-v1
```

## Preconditions

Immediately before evaluation, the solver passed:

- canonical strategy fingerprint recomputation;
- candidate configuration fingerprint recomputation;
- exact tier counts and zero-overlap validation;
- 59,656-identity union validation;
- Python oracle self-test;
- independent JavaScript oracle validation;
- synthetic Unicode end-to-end address agreement;
- synthetic NFKD digest agreement;
- explicit public-puzzle authorization gate.

The repository test suite had also passed all 55 tests.

## Execution boundary

The invocation fixed:

```text
mode = EVALUATE
tier = 1
maximum candidates = 16
processes = 1
automatic next tier = disabled
```

The target, mnemonic, derivation path, and normalization mode were fixed by the
validated Corey oracle and were not supplied as arbitrary CLI inputs.

## Result

```text
Status: TIER_EXHAUSTED
Tier: 1
Tier size: 16
Evaluated successfully: 16
Oracle errors: 0
Matches: 0
Next ordinal: 16
Checkpoint complete: true
Tier 2 started: no
```

No match result file was created.

The final redacted checkpoint evidence is:

```text
last_candidate_id:
0ef203d54150be3963a20b4158c5f1fd1fb0bbaac7bbd8c9d67902c2b4fb6a77

progress_digest:
05e546902eb8e4911112cc78b82ba75b9965ca0c9e3f5fb7268c5f3ddedada1e
```

Deterministic replay of the checkpoint prefix passed after execution.
Checkpoint fields contained no raw or normalized passphrase.

Observed wall time was approximately 5.8 seconds, including full strategy,
partition, Python oracle, and independent JavaScript preflight. It is not a
pure candidate-per-second benchmark and must not be reported as one.

## Interpretation

Tier 1 exhaustion rejects only the 16 exact configured literal identities under
the recorded finite model. It does not prove that the puzzle has no solution,
does not bound the BIP39 passphrase domain, and does not validate any subtraction
from the historical aggregate attempt count.

## Gate after Tier 1

```text
Tier 1: EXHAUSTED — 16/16, no match
Tier 2: NOT STARTED
Tier 3: NOT STARTED
Tier 4: NOT STARTED
Tier 5: NOT STARTED

Automatic progression: DISABLED
Tier 2 authorization: NO-GO
Transactions or fund movement: NO-GO
```

The next possible experiment would be the 24 new case-variant identities in
Tier 2, but it requires a separate explicit gate and must use a new checkpoint.
