# Corey Phillips puzzle: solver-oracle integration gate

## Outcome

The solver now has an explicitly gated evaluation mode for the intentionally
published Corey Phillips reward puzzle. It remains fixed to the existing Corey
oracle and target; it does not accept arbitrary addresses, wallets, derivation
paths, mnemonics, networks, worker counts, or transaction instructions.

No automatic transition between tiers exists.

## Canonical strategy correction

Phase 8 published a strategy fingerprint without publishing the canonical
object or serialization used to calculate it. That fingerprint could be used as
a label but could not be reproduced independently.

The new source of truth is:

```text
research/corey/search-tiers.json
```

Canonical serialization:

```text
JSON parsed object
sort_keys = true
separators = (",", ":")
ensure_ascii = false
encoding = UTF-8
```

Canonical byte length:

```text
2196
```

Reproducible strategy fingerprint:

```text
7f2685ceaeae227a4b85be8431c4c53546b26aa62938f6816282080a7211d61a
```

Superseded contract-only fingerprint:

```text
10940a5429829adfaa6095e44103c628f8fcc046b14c2ca4125925f66b7818bf
```

The canonical object explicitly records the superseded value. The candidate
configuration fingerprint remains unchanged:

```text
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52
```

## Runtime gates

Before an evaluation, the solver must successfully:

1. recompute the canonical strategy fingerprint;
2. recompute the candidate configuration fingerprint;
3. verify `STANDARD_BIP39_NFKD`;
4. reconstruct all five disjoint tier identity sets;
5. verify counts `16 / 24 / 864 / 10,368 / 48,384`;
6. verify zero pairwise overlap and union size 59,656;
7. run the Python oracle protocol and puzzle self-tests;
8. derive one controlled synthetic Unicode passphrase independently in Python
   and JavaScript;
9. require equality of the two derived addresses and normalized candidate
   digests;
10. require an explicit public-puzzle authorization flag.

Any failure stops before the next real candidate.

## Evaluation interface

Evaluation requires:

```text
--evaluate
--authorize-public-puzzle-corey
--tier N
--max-candidates N
--checkpoint PATH | --resume PATH
--result PATH
```

`--max-seconds` may add a second limit. The target and derivation are not CLI
parameters and cannot be redirected to another address.

## Checkpoint semantics

The evaluation checkpoint uses:

```text
corey-phase10-checkpoint-v1
```

After every successful `NO_MATCH` evaluation, the solver atomically commits the
next ordinal, evaluation count, last candidate identity, and chained progress
digest. An oracle `ERROR` does not advance the checkpoint.

On `MATCH`, the solver writes the result exclusively with mode `0600`, refuses
to overwrite an existing result path, commits the matching identity to the
checkpoint, and stops immediately.

Checkpoints contain no plaintext passphrases. Only the separate protected match
result can contain plaintext, and only if a match is found.

## Independent synthetic validation

The following passed before real evaluation authorization:

```text
Synthetic solver self-test: PASS
Independent NFKD identity test: PASS
Synthetic evaluation checkpoint/resume: PASS
Synthetic match stop: PASS
Protected result mode 0600: PASS
Oracle ERROR does not advance checkpoint: PASS
Python oracle self-test: PASS
Independent JavaScript oracle: PASS
Synthetic end-to-end address agreement: PASS
Synthetic NFKD digest agreement: PASS
Canonical strategy fingerprint recomputation: PASS
Real tier candidates evaluated during preflight: 0
```

## Gate

```text
Canonical strategy: GO
Candidate partition: GO
Oracle preflight: GO
Solver-oracle integration: GO
Checkpoint/resume: GO
Explicit public-puzzle authorization control: GO

Authorized next action:
evaluate exactly T1 (16 identities), CPU single-process, then stop

Automatic T2 progression: NO-GO
Transactions or fund movement: NO-GO
```
