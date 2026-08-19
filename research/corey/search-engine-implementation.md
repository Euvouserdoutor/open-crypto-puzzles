# Corey Phillips puzzle: Phase 9 search-engine implementation

## Scope and result

Phase 9 implements a fail-closed tier engine for synthetic validation and
redacted dry runs. It does not connect the candidate generator to the Corey
oracle, accept a target address, derive keys, compare addresses, launch workers,
or authorize a real search.

Implemented artifacts:

- `tools/corey_solver.py`
- `tests/test_corey_solver.py`

The implementation consumes the Phase 8 partition contract:

```text
Candidate configuration fingerprint:
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52

Tier strategy fingerprint:
10940a5429829adfaa6095e44103c628f8fcc046b14c2ca4125925f66b7818bf
```

## Exposed operations

The CLI exposes only:

```text
--selftest
--list-tiers
--dry-run
```

A dry run requires all of:

```text
--tier N
--max-candidates N
--checkpoint PATH | --resume PATH
```

`--max-seconds` is an optional second limit. A single invocation can operate on
only one explicitly selected tier. Completion never advances automatically to
the next tier.

There is no CLI flag for a target, address, oracle, real search, candidate
plaintext, worker count, thread count, GPU, scan, broadcast, or transaction.

## Tier construction

The solver assigns exact candidate identities in fixed precedence order:

| Tier | Source rules | Set-difference result |
|---|---|---:|
| T1 | R001, R002 | 16 |
| T2 | R003 minus prior identities | 24 |
| T3 | R004 minus prior identities | 864 |
| T4 | R005 minus prior identities | 10,368 |
| T5 | R006 minus prior identities | 48,384 |

Before every dry run, the engine fails closed unless it verifies:

- candidate configuration fingerprint equality;
- `STANDARD_BIP39_NFKD` Unicode mode;
- every exact tier count;
- contiguous deterministic tier ordinals;
- zero pairwise tier overlap;
- union size of 59,656 identities;
- complete rule provenance.

Candidate identity remains the generator's exact contract:

```text
SHA256(NFKD(raw_candidate).encode("utf-8"))
```

## Independent self-test

`--selftest` uses only independently constructed synthetic values. It does not
load the puzzle mnemonic, target address, expected puzzle derivation outputs, or
real Corey candidates.

The synthetic checks cover:

- composed/decomposed Unicode equivalence under NFKD;
- exact first-occurrence deduplication;
- disjoint ordered tier assignment;
- deterministic progress digests;
- a fake evaluator with a synthetic match;
- checkpoint schema validation;
- rejection of a changed synthetic fingerprint.

The positive checkpoint test uses independently hashed synthetic configuration
and strategy labels rather than the production fingerprints. This prevents a
self-test from merely comparing a stored production value with itself.

## Checkpoint and resume

Checkpoint schema:

```text
corey-phase9-dry-run-checkpoint-v1
```

Stored fields include:

- solver and schema versions;
- candidate configuration fingerprint;
- tier strategy fingerprint;
- Unicode mode;
- fixed mode `DRY_RUN`;
- one tier number;
- next deterministic ordinal;
- visited unique count;
- evaluated count, fixed at zero in Phase 9;
- last candidate identity;
- chained progress digest;
- completion flag.

No raw or normalized passphrase is written. Resume regenerates the deterministic
prefix and rejects the checkpoint if its last identity or progress digest does
not match. It also rejects configuration, strategy, Unicode, tier, count,
ordinal, mode, or completion inconsistencies.

Writes use a temporary file in the destination directory, file flush and
`fsync`, atomic replacement, and directory `fsync`.

## Limits and termination

`--max-candidates` is mandatory and may be zero. `--max-seconds` may add a
wall-clock limit. Both are checked before the next identity is visited.

Dry-run terminal statuses are deliberately distinct from search coverage:

```text
DRY_RUN_LIMIT_REACHED
DRY_RUN_TIER_COMPLETE
```

The engine does not emit `TIER_EXHAUSTED` or `MODEL_EXHAUSTED`, because no
candidate was evaluated against the target.

## Strategy fingerprint limitation

Phase 8 publishes the strategy fingerprint but does not publish the canonical
strategy object or its byte serialization. Therefore Phase 9 can bind every
checkpoint to the published fingerprint and assert that exact contract value,
but it cannot independently recompute the digest without inventing missing
serialization semantics.

The runtime reports this honestly as:

```text
CONTRACT_ONLY_CANONICAL_OBJECT_NOT_PUBLISHED
```

Independent strategy-fingerprint recomputation remains blocked until the exact
canonical object and serialization are published. This limitation does not
affect the independently verified tier membership and counts, but it prevents a
claim that Phase 8 invariant 10 has been independently reproduced.

## Verification performed

Repository test command:

```text
python -m unittest discover -s tests -v
```

Result:

```text
51 tests passed
```

Phase 9-specific results:

```text
Synthetic self-test: PASS
NFKD/Unicode test: PASS
Independent synthetic checkpoint test: PASS
Tier counts: 16 / 24 / 864 / 10,368 / 48,384
Tier union: 59,656
Pairwise tier overlap: 0
Checkpoint/resume dry run: PASS
Checkpoint plaintext fields: ABSENT
Real-search CLI surface: ABSENT
```

The regression suite exercised existing oracle protocol tests with controlled
fixtures. The Phase 9 solver itself imported no oracle and performed zero real
candidate evaluations.

## Phase 9 gate

```text
Phase 9 implementation: COMPLETE
Synthetic self-test: PASS
NFKD/Unicode requirement: PASS
Independent self-test requirement: PASS
Tier partition runtime validation: PASS
Checkpoint/resume: PASS
Explicit candidate/time limits: PASS
Automatic tier progression: DISABLED
Oracle integration: NOT IMPLEMENTED
Real candidate evaluations by solver: 0
Tier 1 real candidates tested by solver: 0

Independent strategy fingerprint recomputation:
NO-GO — canonical strategy object/serialization not published

Real search authorization: NO-GO
```

## Hard stop

Do not add an oracle adapter, target flag, real-search mode, multiprocessing,
GPU path, or automatic tier progression until a later gate explicitly
authorizes that work. Do not interpret a completed dry run as candidate
coverage.
