# Corey Phillips puzzle: normalization-collision analysis

## Scope and result

This analysis covers candidate text generation and BIP39 protocol
normalization only. It made zero oracle calls, zero target comparisons and zero
cryptographic derivations.

For enabled rules R001–R006 under `STANDARD_BIP39_NFKD`:

| Metric | Count |
|---|---:|
| Raw emissions | 73,492 |
| NFKD-normalized emissions | 73,492 |
| Distinct normalized identities | 59,656 |
| Exact duplicate emissions | 13,836 |
| Distinct-raw NFKD collision events | 0 |
| NFKD collision rate | 0.000000% |

The difference between emissions and unique identities is entirely explained
by exact textual duplicates produced by overlapping style rules. It is not a
Unicode-normalization effect.

## Collision classes

| Class | Observed | Cause | Affected rules | Unicode mode |
|---|---:|---|---|---|
| Canonically equivalent raw strings | 0 | None present in S001/S002 or generated transformations | None | `STANDARD_BIP39_NFKD` |
| Compatibility-equivalent raw strings | 0 | None present in S001/S002 or generated transformations | None | `STANDARD_BIP39_NFKD` |
| Exact textual duplicates | 13,836 events | Rule overlap and internally convergent boundary styles | R001/R003 and R005/R006; internal R006 | Not caused by Unicode |

## Synthetic verification

The controlled test pair `café` and `cafe` followed by U+0301 has different raw
Unicode representations and the same NFKD UTF-8 bytes. The generator's SHA256
identity therefore collapses the pair exactly as BIP39 requires. Case and
whitespace controls remain distinct: `Kitten`, `kitten` and `kitten ` do not
collapse.

No real candidate list is dumped in this report. The synthetic example exists
only to verify the collision detector and normalization boundary.

## Unicode compatibility branches

Phase 5 established that the relevant 2019 implementation normalizes both
mnemonic and passphrase with NFKD. Only `STANDARD_BIP39_NFKD` is justified.
There is no legacy raw-UTF-8 branch and therefore no cross-branch multiplier or
branch overlap to measure.

## Interpretation

Zero observed collisions is a property of the current ASCII-only executable
source corpus, not a proof that future corpora cannot collide. Any recovered
historical corpus or new non-ASCII rule must be re-enumerated through the same
exact identity accounting before its unique count is accepted.
