# Corey Phillips puzzle: candidate-space model

## Scope

This model defines candidate generation and accounting only. It does not derive
keys, call an oracle, compare an address, query a network or perform a search.
Every executable rule is finite, deterministic and traceable to a source or an
explicitly labeled hypothesis.

The author states only that the published image was combined with a BIP39
passphrase. No public clue establishes its length, language, grammar, theme or
whether it is human-memorable. Consequently, even a precisely generated region
does not bound the true passphrase domain.

## Evidence-to-candidate map

| Evidence | Hypothesis | Rule family | Puzzle transformations | Protocol normalization | Identity |
|---|---|---|---|---|---|
| Literal terms and phrases in the author's puzzle materials | A literal may have been reused as the passphrase | Exact literals | None | BIP39 NFKD, UTF-8 | SHA256 of normalized bytes |
| The puzzle is centered on a kitten, an image-to-mnemonic tool and Bitcoin terminology | A short thematic expression may have been chosen | Case and two-token rules | Explicit case and join styles | BIP39 NFKD, UTF-8 | Same |
| The open lead proposes three thematic words | A three-token phrase may have been chosen | Three-token rules | One whole-phrase style or independently selected boundary operations | BIP39 NFKD, UTF-8 | Same |
| Historical reports name 35-token and 108-token corpora | The old thematic regions can be reconstructed | Disabled historical models | Same six named styles | BIP39 NFKD, UTF-8 | Unknown until corpora are recovered |

The first three rows are hypotheses, not passphrase clues. Their source text is
direct evidence; the inference that it supplied the secret is weak.

## Candidate Definitions

### Raw Candidate

The exact Unicode string emitted by a rule before protocol normalization. Case,
punctuation, separators and whitespace are preserved exactly.

### Protocol-Normalized Candidate

The raw candidate after `Unicode NFKD`, encoded as UTF-8. NFKD is the only
protocol transformation.

### Search Candidate

The exact normalized Unicode value whose UTF-8 bytes would eventually be sent
to the verified standards oracle. Phase 6 never performs that submission.

### Candidate Identity

```text
candidate_id = SHA256(NFKD(raw_candidate).encode("utf-8"))
```

This stable 32-byte identity is used for exact deduplication and audit. Python's
process-randomized `hash()` is never used.

## Puzzle transformations versus protocol normalization

Puzzle transformations are explicit rule dimensions: case variants, token
ordering, separators and camel/Pascal operations. They create distinct raw
hypotheses and are counted before normalization.

Protocol normalization is always NFKD. It does not lowercase, uppercase, trim,
collapse spaces, remove punctuation or translate separators. Canonically or
compatibility-equivalent Unicode strings may converge only because BIP39
requires NFKD.

## Unicode policy

Phase 5 verified that the author's 2019 BIP39 bundle applies NFKD to both the
mnemonic and passphrase. There is therefore one candidate-identity branch:

```text
STANDARD_BIP39_NFKD
```

The former raw-UTF-8 compatibility hypothesis is not an enabled generation
branch. This prevents needless duplication of every ASCII candidate. The
historical bundle remains an audit fixture, not a second candidate space.

## Source registries

### S001 — primary-material tokens

The source is deliberately small and explicit, ordered as follows:

```text
kitten, image, bitimage, bitcoin, mnemonic, passphrase,
bip39, segwit, bech32, satoshis, corey, phillips
```

Each token appears in the author-published puzzle, original tool UI/code, or
author attribution. This is a newly versioned corpus; it is not claimed to be
the missing historical 35-token corpus.

### S002 — primary-material phrases

The source contains four exact lowercase textual forms:

```text
a picture is worth a thousand satoshis
not meant to be solved
turn any image or document into a mnemonic phrase
if you somehow manage to claim it congrats
```

Punctuation is omitted only because these are explicitly defined source values,
not because the generator silently strips it. Punctuated variants would require
a separate rule.

## Generation Rule Registry

| Rule ID | Description | Evidence | Confidence | Source | Enabled by default |
|---|---|---|---|---|---|
| R001 | Emit S001 tokens exactly | Direct source terms | MODERATE as source, WEAK as secret hypothesis | S001 | Yes |
| R002 | Emit S002 phrases exactly | Direct source phrases | MODERATE as source, WEAK as secret hypothesis | S002 | Yes |
| R003 | Lower, title-first and upper variants of each S001 token | Common password variation; no author clue | WEAK | S001 | Yes |
| R004 | Ordered S001 token pairs with replacement under six whole-expression styles | Historical two-word model | WEAK | S001; historical rule description | Yes |
| R005 | Ordered S001 token triples with replacement under one of six whole-expression styles | Open three-word lead | WEAK | S001; open lead | Yes |
| R006 | Ordered S001 token triples with replacement and independent operations at both boundaries | Broad interpretation of open lead | SPECULATIVE | S001; prior estimate | Yes |
| R100 | Historical 35-token ordered pairs under six styles | Historical ledger says 7,350 attempts | MODERATE as historical model | Missing 35-token corpus | No |
| R101 | Historical 35-token triples, one style | Prior model `35^3 × 6` | WEAK | Missing 35-token corpus | No |
| R102 | Historical 35-token triples, independent boundaries | Prior model `35^3 × 6^2` | SPECULATIVE | Missing 35-token corpus | No |
| R103 | Historical 108-token triples, one style | Prior model `108^3 × 6` | WEAK | Missing 108-token corpus | No |
| R104 | Historical 108-token triples, independent boundaries | Prior model `108^3 × 6^2` | SPECULATIVE | Missing 108-token corpus | No |

No rule is `CONFIRMED` as a model of the secret because the author published no
passphrase clue. R100–R104 have exact combinatorial raw counts but cannot emit
candidates or establish normalized/unique counts without their source corpora.

## Style semantics and ordering

Styles have stable order:

```text
concat, space, underscore, hyphen, camel, pascal
```

For one whole-expression style:

- `concat`: concatenate stored lowercase tokens;
- `space`, `underscore`, `hyphen`: join with ` `, `_`, or `-`;
- `camel`: keep the first token and title-first each later token;
- `pascal`: title-first every token.

For independent boundaries, operations are folded left-to-right. `camel`
appends a title-first right token. `pascal` title-firsts both the accumulated
left expression and right token. These semantics are a new explicit model; the
historical six-style implementation is unavailable and must not be presumed
identical.

Nested-loop order is rule order, then token positions from left to right, then
style dimensions from left to right. Source order is the literal order above.

## Hypothesis Registry

| Hypothesis | Evidence | Confidence | Candidate rules | Estimated region |
|---|---|---|---|---:|
| H001 | Exact published terms/phrases | WEAK | R001, R002 | 16 raw |
| H002 | Simple token casing | WEAK | R003 | 36 raw |
| H003 | Two-token thematic expression | WEAK | R004 | `12^2 × 6 = 864` raw |
| H004 | Three tokens with one style | WEAK | R005 | `12^3 × 6 = 10,368` raw |
| H005 | Three tokens with independent boundary operations | SPECULATIVE | R006 | `12^3 × 6^2 = 62,208` raw |
| H100 | Missing historical 35-token pair corpus | MODERATE as reconstruction target | R100 | 7,350 raw; unavailable |
| H101 | Historical 35-token triple, one style | WEAK | R101 | 257,250 raw; unavailable |
| H102 | Historical 35-token triple, independent boundaries | SPECULATIVE | R102 | 1,543,500 raw; unavailable |
| H103 | Historical 108-token triple, one style | WEAK | R103 | 7,558,272 raw; unavailable |
| H104 | Historical 108-token triple, independent boundaries | SPECULATIVE | R104 | 45,349,632 raw; unavailable |

## Candidate record and provenance

Each raw emission carries:

```text
CandidateRecord
  global_raw_index
  rule_raw_index
  raw_candidate
  normalized_candidate
  candidate_id
  rule_id
  hypothesis_id
  source_ids
  source_clues
  transformations
  unicode_mode
```

Aggregate output uses fingerprints rather than plaintext. Full raw values may
appear only in a deliberately small developer sample. Provenance is generated
on demand from deterministic coordinates; it is not materialized into a large
metadata file.

## Stable indexing and deduplication

The raw stream receives a global zero-based index before deduplication. The
unique stream receives a second zero-based index in first-occurrence order.
Changing a source, rule, ordering or normalization changes the configuration
fingerprint and defines a new index space.

Exact deduplication stores full 32-byte candidate identities. Approximate
filters cannot support final unique counts. For the current executable region,
an in-memory set is adequate. Larger future regions should use compact sorted
binary fingerprints or a disk-backed exact index.

## Duplicate Taxonomy

- **Exact duplicate:** identical raw UTF-8 bytes.
- **Unicode-equivalent duplicate:** distinct raw strings with the same NFKD
  UTF-8 bytes.
- **Cross-rule duplicate:** the same identity emitted by different rules.
- **Cross-hypothesis duplicate:** the same identity emitted by different
  hypotheses.
- **Historical rerun:** the same candidate evaluated in separate past runs.

First-occurrence deduplication preserves deterministic order. Duplicate events
retain both source coordinates in audit statistics.

## Historical Attempt Audit

Historical attempts: **1,155,064,682**.

Historical unique candidates: **UNKNOWN**.

The total is the arithmetic sum of 11 ledger rows, not a union of candidate
identities. At least 7,454 attempts are explicitly described as an independent
cross-check overlapping earlier families. The alternate-path row counts 432
derivations rather than 432 distinct passphrases, and other list/rule overlaps
cannot be measured. No exact candidate manifests, sorted fingerprints, run
boundaries or normalization metadata are present. Aggregated counts cannot mark
any current identity as previously tested.

`HISTORICAL CANDIDATE SET: UNAVAILABLE`.

## Search Region Reconciliation

| Previous region | Reconstructed raw size | Unique size | Difference | Explanation |
|---:|---:|---:|---|---|
| 257,250 | `35^3 × 6 = 257,250` | UNKNOWN | Raw formula reproduced | Corpus and style implementation unavailable |
| 1,543,500 | `35^3 × 6^2 = 1,543,500` | UNKNOWN | Raw formula reproduced | Same blocker |
| 7,558,272 | `108^3 × 6 = 7,558,272` | UNKNOWN | Raw formula reproduced | 108-token corpus unavailable |
| 45,349,632 | `108^3 × 6^2 = 45,349,632` | UNKNOWN | Raw formula reproduced | Same blocker |

The current 12-token executable model is not a replacement for those regions.
Its purpose is to provide an auditable baseline and validate generation
semantics while historical source recovery remains open.

## Coverage Model

A region is completely generated only when its configuration fingerprint,
source values and order, rule semantics, transformation dimensions,
normalization mode and ordinal interval are all fixed. `EXHAUSTED` would require
the exact unique identity stream to have been processed with checkpointed
coverage; Phase 6 processes none of it through an oracle.

R001–R006 cover only the explicitly listed S001/S002 values and documented
transformations. They exclude arbitrary dictionaries, dates, suffixes,
punctuation, leetspeak, pluralization, substitutions, four-or-more-token phrases
and all missing historical corpus values.

## Configuration fingerprint

The canonical configuration includes schema/generator version, ordered source
values, source evidence labels, ordered hypothesis and rule definitions, style
semantics, ordering, NFKD/UTF-8 policy, candidate-identity algorithm and
deduplication policy. Canonical JSON with sorted object keys and compact
separators is hashed with SHA256.

Any search-relevant semantic change must change this fingerprint.

## Measured executable-space totals

The enabled R001–R006 configuration has fingerprint:

```text
41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52
```

It emits 73,492 raw candidates and 73,492 protocol-normalized emissions.
Exact first-occurrence deduplication leaves 59,656 unique identities. The
13,836 duplicate emissions are exact textual duplicates; no distinct raw
strings collide under NFKD in this corpus. Evidence rules R001–R002 contribute
16 unique identities. Hypothesis rules R003–R006 contribute 59,652 unique
identities, 12 of which overlap the evidence set.

These figures describe only the explicit 12-token/four-phrase model. They do
not convert the missing historical regions into known spaces and do not bound
the possible BIP39 passphrase.
