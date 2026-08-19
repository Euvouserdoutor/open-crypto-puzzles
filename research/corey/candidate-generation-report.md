# Corey Phillips puzzle: Phase 6 candidate-generation report

## 1. Implementation summary

`tools/corey_candidates.py` is a deterministic, lazy candidate generator and
accounting tool. It contains no target address, key derivation, oracle import,
network operation, concurrency or search interface. Its CLI is limited to
registry inspection, counting, statistics, bounded samples and a synthetic
self-test.

The candidate flow is:

```text
evidence -> hypothesis -> rule -> explicit puzzle transformation
         -> NFKD -> UTF-8 -> SHA256 identity -> exact first-occurrence dedup
```

The executable model is deliberately small because the historical 35-token
and 108-token corpora are absent. It is an auditable baseline, not a claim that
the true passphrase lies inside this region.

## 2. Generation rules

| Rule | Hypothesis | Raw | NFKD emissions | Unique within rule | Internal duplicate events | Unique overlap with prior rules | Marginal unique |
|---|---|---:|---:|---:|---:|---:|---:|
| R001 | H001 | 12 | 12 | 12 | 0 | 0 | 12 |
| R002 | H001 | 4 | 4 | 4 | 0 | 0 | 4 |
| R003 | H002 | 36 | 36 | 36 | 0 | 12 | 24 |
| R004 | H003 | 864 | 864 | 864 | 0 | 0 | 864 |
| R005 | H004 | 10,368 | 10,368 | 10,368 | 0 | 0 | 10,368 |
| R006 | H005 | 62,208 | 62,208 | 58,752 | 3,456 | 10,368 | 48,384 |
| **Total/union** | | **73,492** | **73,492** | — | **3,456 internal** | — | **59,656** |

R100–R104 are registered but disabled. Their raw formulas are known; their
candidate streams and unique counts are unavailable because source values and
historical transformation semantics are missing.

## 3. Hypothesis registry and counts

| Hypothesis | Confidence | Rules | Raw | Unique in hypothesis | New vs prior hypotheses | Overlap with prior |
|---|---|---|---:|---:|---:|---:|
| H001 literals | WEAK | R001–R002 | 16 | 16 | 16 | 0 |
| H002 casing | WEAK | R003 | 36 | 36 | 24 | 12 |
| H003 two tokens | WEAK | R004 | 864 | 864 | 864 | 0 |
| H004 three tokens, one style | WEAK | R005 | 10,368 | 10,368 | 10,368 | 0 |
| H005 independent boundaries | SPECULATIVE | R006 | 62,208 | 58,752 | 48,384 | 10,368 |
| H100 historical 35-token pairs | MODERATE reconstruction | R100 | 7,350 | UNKNOWN | UNKNOWN | UNKNOWN |
| H101 historical 35-token triples | WEAK | R101 | 257,250 | UNKNOWN | UNKNOWN | UNKNOWN |
| H102 historical 35-token independent boundaries | SPECULATIVE | R102 | 1,543,500 | UNKNOWN | UNKNOWN | UNKNOWN |
| H103 historical 108-token triples | WEAK | R103 | 7,558,272 | UNKNOWN | UNKNOWN | UNKNOWN |
| H104 historical 108-token independent boundaries | SPECULATIVE | R104 | 45,349,632 | UNKNOWN | UNKNOWN | UNKNOWN |

No hypothesis is confirmed as a property of the secret. The puzzle's primary
materials are evidence; reusing their words as the passphrase is an inference.

## 4. Candidate-space totals

| Space | Raw emissions | Protocol-normalized emissions | Exact unique identities |
|---|---:|---:|---:|
| Evidence-backed rules R001–R002 | 16 | 16 | 16 |
| Hypothesis-backed rules R003–R006 | 73,476 | 73,476 | 59,652 |
| Enabled union R001–R006 | 73,492 | 73,492 | 59,656 |

The evidence and hypothesis unique sets overlap by 12 identities, so their
unique counts must not be added. “Protocol-normalized emissions” counts every
raw emission after NFKD; “exact unique identities” is the deduplicated space.

## 5. Duplicate statistics

The enabled stream has 13,836 duplicate emissions, an exact duplicate rate of
18.826538943%. All are byte-for-byte textual duplicates. There are zero
distinct-raw NFKD collisions, for a normalization-collision rate of 0%.

R006 contains 3,456 internal duplicate events because different sequences of
boundary operations can converge to the same text. Separately, its identity
set overlaps R005 by 10,368. R003 overlaps R001 by 12.

## 6. Cross-rule overlap

Only non-zero intersections are shown.

| Left | Right | Shared identities | Share of smaller rule |
|---|---|---:|---:|
| R005 | R006 | 10,368 | 100% |
| R001 | R003 | 12 | 100% |

R005 is a complete subset of R006 under the explicit style semantics. R001's
lowercase literals are a complete subset of R003.

## 7. Cross-hypothesis overlap

| Left | Right | Shared identities | Share of smaller hypothesis |
|---|---|---:|---:|
| H004 | H005 | 10,368 | 100% |
| H001 | H002 | 12 | 75% |

All other enabled hypothesis-pair intersections are zero. A future ordered
process can therefore evaluate only each hypothesis's marginal identities.
This report does not perform that evaluation.

## 8. Unicode collision statistics

The only justified mode is `STANDARD_BIP39_NFKD`. Phase 5 eliminated a
separate legacy behavior branch. Current sources and transformations are ASCII,
so all 73,492 normalized emissions preserve their raw text and no NFKD collision
class occurs. Synthetic canonical-equivalence tests pass. Full details are in
`normalization-collisions.md`.

## 9. Historical-attempt interpretation

Historical attempts: **1,155,064,682**.

Historical unique candidates: **UNKNOWN**.

The figure is a sum of ledger attempts, not a union of identities. At least
7,454 attempts are explicitly overlapping cross-check work. A 432-count row
describes derivations rather than established unique passphrases. The repository
has no candidate manifests, complete run records, normalized fingerprints or
the 35/108-token corpora. Historical aggregate counts cannot exclude any
current identity.

`HISTORICAL CANDIDATE SET: UNAVAILABLE`.

## 10. Search Region Reconciliation

| Previous region | Reconstructed raw size | Exact unique size | Status |
|---:|---:|---:|---|
| 257,250 | `35^3 * 6 = 257,250` | UNKNOWN | Raw formula reproduced; corpus missing |
| 1,543,500 | `35^3 * 6^2 = 1,543,500` | UNKNOWN | Raw formula reproduced; corpus missing |
| 7,558,272 | `108^3 * 6 = 7,558,272` | UNKNOWN | Raw formula reproduced; corpus missing |
| 45,349,632 | `108^3 * 6^2 = 45,349,632` | UNKNOWN | Raw formula reproduced; corpus missing |

The reconstructed historical raw range remains 257,250–45,349,632. It is not
implemented because raw formulas alone cannot recover candidate identities.

## 11. Determinism, indexing and provenance

Configuration fingerprint:

```text
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52
```

The raw stream has stable zero-based global and per-rule indices. The unique
stream has a stable zero-based first-occurrence index. Reproduction requires
the same code, configuration fingerprint and ordered registries. Each record
retains rule, hypothesis, sources, evidence labels, transformations, Unicode
mode and candidate identity. Provenance is regenerated on demand instead of
stored as a plaintext corpus.

## 12. Memory and runtime characteristics

Generation itself is lazy and bounded by the current record. Exact aggregate
deduplication and overlap statistics retain SHA256 identities in Python sets.
On the available CPU, five complete statistics runs over 73,492 emissions
measured 136,645–203,369 raw candidates/second, with a median of 165,814/second.
The median elapsed time was 0.443 seconds. Peak resident memory observed across
those runs was about 57,980 KiB; a single run observed about 56,200 KiB.

These are candidate-generation/deduplication measurements only. No PBKDF2,
address derivation or oracle performance was measured. For the present space,
an in-memory exact set is simplest. At tens of millions of candidates, compact
binary fingerprints, external sorting or a disk-backed exact index should be
evaluated; Bloom filters cannot establish exact coverage.

## 13. Validation

- Python compilation: PASS.
- Unit tests: 20 PASS, synthetic/structural data only for generation logic.
- Generator `--selftest`: PASS for registry, determinism, normalization,
  identity, configuration sensitivity and count consistency.
- Repeated configuration fingerprint: stable.
- Real oracle calls: 0.
- Real puzzle target comparisons: 0.
- Real candidate search: NO.

## 14. Unresolved candidate-space assumptions

- The true passphrase length, language, grammar and theme are unconstrained.
- S001/S002 are new explicit source sets, not recovered historical corpora.
- The historical six style operations and their ordering are not available.
- Historical candidate identities, normalization metadata and rerun boundaries
  are unavailable.
- No current evidence justifies punctuation, dates, suffixes, substitutions,
  leetspeak, pluralization or four-or-more-token expansion.

## 15. Blockers for Phase 7

Phase 7 search-space reduction can proceed on the documented model, because
rules, confidence, marginal counts and overlap are explicit. It must preserve
the following blockers rather than treating them as solved:

- recover or explicitly abandon the missing 35-token and 108-token corpora;
- distinguish model prioritization from evidence about the secret;
- never use 1,155,064,682 aggregate attempts to exclude identities;
- require a new configuration fingerprint after any source/rule change.

This gate authorizes reduction and prioritization analysis only. It does not
authorize oracle evaluation or brute force.
