# Corey Phillips kitten passphrase: solver specification

This is the implementation contract for a verifier and, later, a bounded candidate-search
engine for the intentionally published Corey Phillips kitten puzzle. It specifies the
target and computation but does not implement a solver, enumerate real candidates, or
start a search.

Status vocabulary used throughout:

- `CONFIRMED`: reproduced locally or directly stated by primary puzzle evidence.
- `INFERRED`: follows strongly from confirmed evidence but is not stated directly.
- `UNVERIFIED`: reported by secondary research or historical logs that cannot be fully
  reproduced from the files currently present.
- `CONFLICTING`: relevant sources or implementations disagree.
- `UNKNOWN`: the available evidence does not determine the value.

## Source of Truth

### Evidence priority

1. The author's published article/code and the exact published puzzle artifact.
2. Reproducible cryptographic results from the archived artifact.
3. The puzzle's `puzzle.json`, `README.md`, and current oracle source.
4. The negative-search ledger and derived research.
5. Hypotheses in `analysis/leads.md` and `research/corey/attack-plan.md`.

Derived research never overrides contradictory primary evidence.

| Source | Role | Reliability for this specification |
|---|---|---|
| `clues/kitten.jpeg` | Exact public puzzle artifact | `CONFIRMED`; artifact SHA-256 matches `puzzle.json` |
| `clues/author-posts.md` | Short primary quotes and links; community hints | Author quotes are `CONFIRMED`; community statements are secondary |
| Author's linked 2019 article and `bitimage` code | Original mechanism and target announcement | Primary, but the exact 2019 dependency versions are `UNKNOWN` |
| `puzzle.json` | Structured target, prize and derivation claims | Consistent with the folder README; escrow state is only a dated snapshot |
| `README.md` | Narrative synthesis | Strong secondary source; some “certified” wording is broader than the current self-test proves |
| `tools/oracle.py` | Executable derivation currently used | `CONFIRMED` for its exact source behavior; not automatically proof of BIP39 conformance |
| `analysis/tested.md` | Historical negative-run ledger | Counts and runs are `UNVERIFIED` from this checkout because candidate/run artifacts are absent |
| `analysis/leads.md` | Proposed next hypotheses | `INFERRED` or `UNVERIFIED`, never a source of cryptographic truth |
| `data/coverage.csv` | Aggregated attempt counts | Reproduces the reported arithmetic, not unique-candidate coverage |
| `data/pipeline-stages.json` and figures | Visual summaries | Derived documentation only |
| `research/corey/attack-plan.md` | Prior reverse engineering and planning | Derived; useful but audited rather than presumed correct |
| Root `puzzles.json` | Generated copy of all manifests | Parsed successfully; contains exactly one matching slug and agrees with folder `puzzle.json` |

### Material findings and provenance

| Finding | Status | Evidence |
|---|---|---|
| The puzzle is a public, intentional reward challenge | `CONFIRMED` | Author quote in `clues/author-posts.md`; root disclaimer |
| The exact JPEG produces the recorded entropy and mnemonic | `CONFIRMED` | Artifact plus author mechanism; reproduced digest; folder README |
| The target is a Bitcoin mainnet P2WPKH address | `CONFIRMED` | Published address, valid Bech32 decode, `tools/oracle.py` |
| The primary path is `m/84'/0'/0'/0/0` | `CONFIRMED` | Author pseudocode summarized in `clues/author-posts.md`; README; oracle constant |
| The only primary-model unknown is the BIP39 passphrase | `CONFIRMED` | Author quote, fixed image/mnemonic, published derivation |
| The passphrase follows a human-memorable theme | `UNKNOWN` | No published length, language, grammar or theme clue |
| The current oracle is fully BIP39-conformant for Unicode | `CONFLICTING` | BIP39 requires NFKD; `seed_from_passphrase` uses raw UTF-8 |
| The self-test recomputes the image and mnemonic | `CONFLICTING` | README says it does; current `selftest()` uses a hard-coded mnemonic and never reads the image |
| Exactly 1,155,064,682 unique passphrases were excluded | `UNVERIFIED` | Ledger totals attempts and includes an overlapping cross-check; source candidate manifests are absent |
| The target was funded and unspent on 2026-08-16 | `CONFIRMED` as a dated snapshot | `puzzle.json` and README |
| The target is funded at the start of a future run | `UNKNOWN` until rechecked | Blockchain state can change |

## Target Definition

| Field | Value | Status | Evidence |
|---|---|---|---|
| Blockchain | Bitcoin | `CONFIRMED` | `puzzle.json`, author article |
| Network | Bitcoin mainnet | `CONFIRMED` | HRP `bc`, coin type `0'`, oracle |
| Published target | `bc1qcyrndzgy036f6ax370g8zyvlw86ulawgt0246r` | `CONFIRMED` | Author quote, manifest, README |
| Address type | Native SegWit v0 P2WPKH, BIP173 Bech32 | `CONFIRMED` | Successful decode; 20-byte witness program |
| Witness version | `0` | `CONFIRMED` | Address decode |
| Witness program / HASH160 | `c1073689047c749d74d1f3d071119f71f5cff5c8` | `CONFIRMED` | Local address decode |
| scriptPubKey | `0014c1073689047c749d74d1f3d071119f71f5cff5c8` | `CONFIRMED` | `OP_0` plus 20-byte program |
| Originally announced reward | `0.01 BTC` | `CONFIRMED` | Author quote |
| Dated recorded balance | `1,001,900 sats`, zero spent on 2026-08-16 | `CONFIRMED` as snapshot | `puzzle.json` |
| Objective | Find the BIP39 passphrase which, with the fixed mnemonic and path, derives the target | `CONFIRMED` | Author quote and reproducible pipeline |

The final target is an address, equivalently the SegWit v0 script shown above. It is not
an xpub, public key, private key or free-standing hash. A solution is exactly:

```text
bech32_p2wpkh(derive(mnemonic, candidate, m/84'/0'/0'/0/0))
== bc1qcyrndzgy036f6ax370g8zyvlw86ulawgt0246r
```

No partial, checksum-only, prefix, balance, similarity or “near match” result qualifies.

## Known Secret Material

The term “secret material” here describes key-derivation inputs. The known values are
public because the author intentionally published the puzzle.

| Field | Value | Status | Evidence |
|---|---|---|---|
| Image SHA-256 | `b988e0881a0211222e83f3e2a4bfac695c951bf96aa33ec112fab6992f5e7343` | `CONFIRMED` | Artifact and manifest |
| Image-derived entropy | `1808d35318ac7cb98b69ff9779b699d6a631f15e0b353ac89b7c4020774832ed` | `CONFIRMED` | `SHA256(base64(JPEG bytes))` reproduced locally |
| Mnemonic size | 24 words | `CONFIRMED` | BIP39 derivation and README |
| BIP39 language | English | `CONFIRMED` | Every word indexes the English BIP39 list |
| Mnemonic | `blossom educate state course sick fresh color divide number soap please pull glide weather join grit depart dynamic tenant leopard alter piano slight room` | `CONFIRMED` | Reproduced from entropy; oracle constant |
| BIP39 passphrase | Not known | `UNKNOWN` | Sole puzzle variable |
| BIP39 seed | Not known for the target | `UNKNOWN` | Depends on passphrase |
| BIP32 network | Bitcoin mainnet | `CONFIRMED` | Address and path |
| BIP32 path | `m/84'/0'/0'/0/0` | `CONFIRMED` for primary model | Author mechanism and oracle |
| Purpose | `84'` | `CONFIRMED` | Path |
| Coin type | `0'` | `CONFIRMED` | Path |
| Account | `0'` | `CONFIRMED` | Path |
| Change | `0` | `CONFIRMED` | Path |
| Address index | `0` | `CONFIRMED` | Path |
| Target public/private key | Unknown | `UNKNOWN` | Depends on passphrase |
| Target xpub/fingerprint | Unknown | `UNKNOWN` | Depends on passphrase |

The empty-passphrase sister address is public calibration data, not the prize target.

## Unknown Variables

### Primary model

```text
P = the BIP39 passphrase supplied to mnemonic-to-seed derivation
```

| Property | Definition |
|---|---|
| Type | Unicode string |
| Protocol encoding | UTF-8 after NFKD normalization |
| Domain | All finite Unicode strings representable by the original implementation |
| Empty value | Valid protocol input, but confirmed to derive the sister address, not the target |
| Case | Significant after NFKD |
| Whitespace | Significant; no trimming or collapsing is specified by BIP39 |
| Length | `UNKNOWN`; no evidence-backed minimum or maximum |
| Language | `UNKNOWN` |
| Word count | `UNKNOWN`; “25th word” does not imply exactly one dictionary word |
| Character set | `UNKNOWN` |
| Confirmed clue constraints | None beyond being the passphrase used by the author |
| Confidence that P is the sole variable | High for the primary derivation |

### Compatibility variable

```text
M = passphrase normalization semantics used by the author's exact 2019 bip39 dependency
```

`M` should be NFKD under BIP39, but the exact dependency version has not been pinned and
the current oracle uses raw UTF-8. For ASCII, both semantics are identical. For non-ASCII,
the future oracle must distinguish a standards lane (`M = NFKD`) from a legacy-compatibility
lane (`M = raw`) until the 2019 implementation is verified.

Alternative derivation paths are hypotheses, not unresolved variables in the primary
model. They must never be silently mixed into passphrase coverage claims.

## Cryptographic Pipeline

Let `F` be the exact bytes of `clues/kitten.jpeg` and `P` one candidate.

1. `B = RFC4648_Base64(F)`, with no data-URI prefix, whitespace or trailing newline.
2. `E = SHA256(B)`. The confirmed 32-byte result is the entropy above.
3. `M24 = BIP39_English_EntropyToMnemonic(E)`. With 256-bit entropy, append the first
   eight bits of `SHA256(E)`, split 264 bits into 24 eleven-bit indices, then map through
   the English BIP39 list.
4. `password = UTF8(NFKD(M24))`.
5. `salt = UTF8("mnemonic" || NFKD(P))` in the standards lane. The compatibility lane
   instead uses `b"mnemonic" || UTF8(P)` exactly as the current oracle does.
6. `seed = PBKDF2-HMAC-SHA512(password, salt, iterations=2048, dkLen=64)`.
7. `I = HMAC-SHA512(key=b"Bitcoin seed", data=seed)`; parse its halves as master private
   scalar `k_m` and chain code `c_m`.
8. Derive private children along `84' / 0' / 0' / 0 / 0` with BIP32 CKDpriv:
   hardened input is `0x00 || ser256(k_parent) || ser32(index)`; non-hardened input is
   `serP(point(k_parent)) || ser32(index)`. At each step, HMAC-SHA512 is keyed by the
   parent chain code and `k_child = (parse256(IL) + k_parent) mod n`.
9. Apply BIP32 invalid-child handling if `parse256(IL) >= n` or the child scalar is zero.
   The current oracle omits these checks; the probability is negligible, but the verifier
   contract must be standards-correct.
10. Serialize the final secp256k1 public point in 33-byte compressed form.
11. `program = RIPEMD160(SHA256(compressed_pubkey))`.
12. Build SegWit version 0 data, convert the 20-byte program from 8 to 5 bits with padding,
   and encode with mainnet HRP `bc` and the BIP173 Bech32 constant.
13. Compare the generated address exactly with the published target.

Candidate generation is outside this cryptographic function and must never alter the
candidate invisibly.

## Derivation Path

The primary path is:

```text
m / 84' / 0' / 0' / 0 / 0
```

| Level | Index | Mode | Meaning |
|---|---:|---|---|
| Purpose | 84 | Hardened | Native SegWit convention |
| Coin | 0 | Hardened | Bitcoin mainnet |
| Account | 0 | Hardened | First account |
| Change | 0 | Normal | External chain |
| Address | 0 | Normal | First address |

This path is not merely inferred from the `bc1` format: it is present in the published
mechanism and the current oracle. The alternate BIP44/BIP49 lead is a low-priority author
implementation-mismatch experiment. If ever executed, it must say whether it means:

- standard BIP44/BIP49 path plus standard P2PKH/P2SH-P2WPKH encoding, whose textual
  addresses cannot equal this Bech32 target; or
- keys derived at the 44'/49' paths but deliberately encoded as P2WPKH, which can be
  compared with the target but is not a standard BIP44/BIP49 address derivation.

## Candidate Normalization

### Protocol-mandated transformation

```text
normalize_protocol(candidate) = UTF8(NFKD(candidate))
```

NFKD is mandatory in the standards lane. This is compatible with case and whitespace
sensitivity: NFKD does not mean lowercase, trimming or whitespace collapsing.

### Transformations that are forbidden as silent normalization

- lowercasing or uppercasing;
- trimming leading or trailing whitespace;
- collapsing or translating whitespace;
- stripping punctuation, accents, symbols or emojis;
- inserting/removing separators;
- converting hyphens and underscores;
- changing decimal representations;
- applying leetspeak, camelCase or PascalCase.

Those operations create distinct candidates and belong in a documented generator rule.
They must affect N and candidate order.

### Candidate identity

In the standards lane, two source strings are duplicates if their NFKD UTF-8 bytes are
identical. In the raw compatibility lane, identity is exact UTF-8 bytes. Line-oriented
input must remove only the record delimiter; it must not accidentally erase candidate
whitespace. An implementation that cannot represent a candidate exactly must return
`ERROR`, not silently transform it.

## Oracle Contract

The future `tools/corey_oracle.py` implements:

```text
verify(candidate: UnicodeString, mode: standards|raw-compat) -> MATCH|NO_MATCH|ERROR
```

### Input

- Exactly one Unicode string per invocation.
- Strict UTF-8 at external boundaries; malformed input is `ERROR`.
- Empty string is valid.
- Embedded NUL/newline handling must be explicit. Shell positional arguments are a
  convenience, not the canonical programmatic interface.
- Any operational size limit is not a puzzle constraint. Exceeding it returns `ERROR`,
  never `NO_MATCH`.
- Default mode is `standards`; `raw-compat` must be explicit and labeled.

### Output and exit status

| Result | stdout | Exit |
|---|---|---:|
| Exact target | `MATCH` | 0 |
| Valid non-match | `NO_MATCH` | 1 |
| Invalid input/internal failure | `ERROR` | 2 |

Normal mode prints no candidate, mnemonic, seed, key, derived address or exception trace.
Diagnostic data is allowed only behind an explicit local debug flag and must follow the
redaction policy below.

### Invariants

- Same candidate, mode and pinned implementation always produce the same result.
- Verification is fully local after dependencies are installed.
- The target is compiled/configured as this one published address; arbitrary target input
  is not accepted in normal operation.
- The oracle never enumerates, mutates or guesses candidates.
- It never queries balances, scans addresses, accesses unrelated wallets, broadcasts or
  signs a transaction.
- A derivation or dependency failure is never converted into `NO_MATCH`.

## Intermediate Derivation Values

Debug mode may expose only what is necessary to compare implementations:

| Stage | Safe diagnostic value |
|---|---|
| Candidate input | Length, mode, and SHA-256 of seed-effective candidate bytes; plaintext only with a separate explicit unsafe-local flag |
| Image | File SHA-256 and `SHA256(base64(file))` |
| Mnemonic | SHA-256 and word count; full public mnemonic only when explicitly requested |
| BIP39 seed | SHA-256 of seed, never the full seed in routine logs |
| Master node | Four-byte BIP32 master fingerprint, never xprv/private scalar |
| Derived node | Compressed public key or its SHA-256; never private scalar |
| Address payload | HASH160/witness program and scriptPubKey |
| Final | Generated and expected addresses |

Puzzle-specific empty-passphrase diagnostics reproduced locally:

| Value | Expected | Status |
|---|---|---|
| Seed SHA-256 | `d93411b7863f34d244eb36508e5ca56466ddffcdb66955d8121d273493124d80` | `CONFIRMED` by current derivation; independent comparison still required |
| Master fingerprint | `d7769df5` | Same status |
| Child compressed pubkey | `021209b131dfbd1efcfe15b1d1e92002653f5fc98e9ff6cb73a0d70153dbe58463` | Same status |
| Child HASH160 | `a7b3cbaa248820a495b4dadc1e9a9f0670960db6` | Same status |
| Sister address | `bc1q57euh23y3qs2f9d5mtwpax5lqecfvrdkqce82a` | `CONFIRMED` against published value |

## Independent Validation Plan

### Implementation A: explicit reference pipeline

Use a minimal, readable implementation with standard-library PBKDF2/HMAC/hash functions,
one pinned secp256k1 library, explicit BIP32 CKDpriv, and explicit Bech32 encoding. It must
recompute the mnemonic from the image rather than trusting the hard-coded string.

### Implementation B: author-compatible library pipeline

Use a separately maintained, pinned implementation of BIP39, BIP32 and Bitcoin address
encoding, preferably the JavaScript library family used by the author's published code.
No cryptographic derivation code should be copied from Implementation A.

### Required agreement

For protocol vectors and each puzzle calibration candidate:

```text
entropy_A             == entropy_B
mnemonic_A            == mnemonic_B
seed_hash_A           == seed_hash_B
master_fingerprint_A  == master_fingerprint_B
child_pubkey_A         == child_pubkey_B
HASH160_A              == HASH160_B
address_A              == address_B
```

Compare both composed and decomposed Unicode representations. If the exact 2019 library
produces raw rather than NFKD behavior, preserve that as a separately named compatibility
result; do not redefine standard BIP39.

The oracle becomes `VERIFIED` only after both methods agree on protocol vectors, the
empty-passphrase puzzle vector, at least one non-empty ASCII candidate, and Unicode NFKD
equivalence. A test suite that calls the same implementation twice is not independent.

## Test Vectors

### Protocol test vectors

| Layer | Required vector family | Purpose |
|---|---|---|
| BIP39 entropy/mnemonic/seed | Official BIP39 vectors, including the `TREZOR` passphrase | Entropy mapping, checksum, PBKDF2 |
| BIP39 Unicode | Official Japanese normalization vector plus locally paired composed/decomposed strings | Prove NFKD behavior |
| PBKDF2-HMAC-SHA512 | Published PBKDF2 vectors or independent library output | Isolate seed derivation |
| BIP32 | Official BIP32 vector 1 and invalid-child handling tests | Hardened and non-hardened CKD |
| secp256k1 | Library's published scalar-to-compressed-public-key vectors | Public-key serialization |
| Bech32 SegWit v0 | Official BIP173 valid and invalid address vectors | Witness conversion, checksum and rejection |

Exact vector payloads should be imported or linked from authoritative sources at
implementation time rather than manually transcribed into this specification.

### Puzzle-specific vectors

1. Exact JPEG SHA-256 equals the artifact value.
2. SHA-256 of its base64 bytes equals the public entropy.
3. Entropy-to-mnemonic equals the fixed 24-word mnemonic.
4. Empty passphrase derives the sister address and intermediate diagnostics above.
5. `control_test_pw_42` currently derives
   `bc1q9ca0na6ytv6xr0mgjrva843224gakwaklgwenu`; this is `UNVERIFIED` until Implementation
   B agrees.
6. No known passphrase-to-prize-address positive vector exists: `NO KNOWN TEST VECTOR`.

The existing self-test is insufficient because it does not read the image, does not test
Unicode normalization, does not compare intermediate values independently, and its
negative control proves only that one arbitrary candidate is not the target.

## Search Space Model

### Naive search space

All finite Unicode strings form a countably infinite set. The protocol supplies no finite
length or alphabet, so the naive search space is **unbounded**, not merely large. A finite
mask must state its alphabet and length; for example, printable ASCII strings of exactly
eight characters contain `95^8 = 6,634,204,312,890,625` candidates.

### Evidence-constrained search space

The evidence fixes the mnemonic, path, network and target but supplies no confirmed
passphrase length, alphabet, language, grammar or source. Therefore the evidence-constrained
passphrase space remains **unbounded**. Calling the puzzle a “bounded target” describes
deterministic verification, not a bounded passphrase domain.

The following areas are reported as attempted, not available search constraints:

- 14,343,467 raw `rockyou` entries;
- 1,104,459,484 `rockyou` + best64 attempts;
- 23,735,781 Corey-corpus attempts;
- 2,808,334 in-joke attempts;
- other documented lists and combinators.

Because the actual candidate manifests are absent and one listed cross-check overlaps
other families, `1,155,064,682` is best described as recorded derivation attempts, not a
certified count of unique excluded passphrases.

### Hypothesis-constrained regions

For a recovered 35-token thematic corpus, ordered selection with replacement gives:

| Hypothesis | Formula | Raw N |
|---|---:|---:|
| Three words, one whole-phrase style among six | `35^3 * 6` | 257,250 |
| Three words, two independently selected boundary styles | `35^3 * 6^2` | 1,543,500 |

For a recovered 108-token author corpus:

| Hypothesis | Formula | Raw N |
|---|---:|---:|
| Three words, one style | `108^3 * 6` | 7,558,272 |
| Three words, independent boundaries | `108^3 * 6^2` | 45,349,632 |

These are hypotheses, not current executable spaces: the corpora and precise three-word
style semantics are missing. Deduplication will reduce the unique N. Every further rule
(dates, suffixes, punctuation or case variants) is a separately counted multiplier.

## Early-Rejection Opportunities

| Filter | Cost | Expected reduction | False-negative risk | Evidence |
|---|---:|---:|---|---|
| Reject malformed external UTF-8 as `ERROR` | Very low | Input dependent | None for representable candidates | Interface correctness |
| Deduplicate identical seed-effective bytes | Low to moderate | Unknown | None with exact storage | Cryptographic equivalence |
| Skip empty passphrase after self-test | Very low | One candidate | None | It derives the sister address |
| Subtract exact prior candidates | Moderate | Potentially large | None only with recovered exact manifests | Current manifests absent |
| Enforce a maximum operational input size as `ERROR` | Very low | Unknown | Does not claim non-match, but leaves region untested | Resource safety only |
| Restrict language, length, alphabet or word count | Low | Potentially huge | High | No confirmed constraint |
| Lowercase, trim, collapse spaces or strip punctuation | Low | Unknown | Unacceptable | Contradicts passphrase sensitivity |
| Compare partial address prefixes before full derivation | No useful saving | Negligible | None if exact comparison follows | Address exists only after expensive derivation |

No checksum-like property of the passphrase permits safe pre-PBKDF2 rejection. Candidate
generation and exact deduplication are the only meaningful cheap stages currently known.

## Computational Cost Model

Per candidate, the solver performs:

1. candidate generation and NFKD/UTF-8 conversion;
2. PBKDF2-HMAC-SHA512 with 2,048 iterations;
3. one master HMAC-SHA512;
4. five BIP32 child HMAC-SHA512 operations;
5. public-key operations for two non-hardened child inputs plus the final public key;
6. SHA-256, RIPEMD-160 and Bech32 encoding;
7. exact address comparison and metrics/checkpoint accounting.

Before profiling, the expected dominant costs are PBKDF2, secp256k1 scalar multiplication,
and interpreter/foreign-function overhead. Candidate generation and address encoding are
expected to be minor for ordinary strings, but all classifications remain hypotheses until
measured in the benchmark/profile phase.

Existing measurements are context, not a promised solver rate:

- current single-process Python oracle: approximately 343 candidates/s on one host;
- PBKDF2-only on that host: approximately 1,094/s;
- historical optimized CPU engine: 12,700/s (`UNVERIFIED` here);
- historical GPU: 315,000–690,000/s (`UNVERIFIED` here).

## Solver Architecture

| Component | Responsibility | Input | Output/state | Errors |
|---|---|---|---|---|
| `PuzzleDefinition` | Immutable target, network, path, mnemonic/artifact hashes | Versioned config | Validated constants | Target/config mismatch |
| `CandidateSource` | Expose a versioned corpus/template definition | Corpus/rule manifests | Deterministic source records | Missing/hash-mismatched source |
| `CandidateGenerator` | Expand one documented hypothesis in exact order | Source records, rule, ordinal | Candidate plus generator coordinates | Undefined/non-deterministic rule |
| `CandidateNormalizer` | Apply only selected protocol lane | Unicode candidate | Seed-effective bytes, identity | Encoding/normalization error |
| `CandidateFilter` | Exact dedup and safe exclusions | Candidate identity | Accept/reject with reason | Storage corruption |
| `BatchScheduler` | Partition disjoint ordinal ranges | N, batch/shard config | Ordered batches | Gap/overlap/worker loss |
| `KeyDeriver` | BIP39 seed and BIP32 path | Effective candidate bytes | Public derivation diagnostics | Invalid child/dependency failure |
| `AddressOracle` | Encode and compare fixed target | Derived public key | `MATCH`/`NO_MATCH`/`ERROR` | Encoding/target failure |
| `MatchVerifier` | Re-run candidate in independent implementation | Match candidate held in memory | `VERIFIED_MATCH` or error | Cross-check disagreement |
| `CheckpointManager` | Atomic, fingerprint-bound progress | Search state | Durable checkpoint | Corruption/fingerprint mismatch |
| `MetricsReporter` | Non-sensitive counts/rates/status | Counters/timers | Logs/summary | I/O failure |

The oracle remains independently callable and contains no generator. The production
solver may optimize internals, but every optimized result must remain cross-checkable
against the reference oracle.

## Determinism Requirements

```text
same source bytes + same rules + same configuration + same checkpoint = same order
```

- Corpus order is defined by exact file bytes and explicit decoding/newline rules.
- Generator products use documented nested-loop order and stable rule order.
- Deduplication preserves first occurrence.
- Shards are disjoint half-open ordinal intervals `[start, end)`.
- Batch size does not change global ordinal assignment.
- No unordered set/dictionary iteration may define search order.
- Randomization is avoided. If a ranked model requires it, its algorithm, model hash and
  fixed seed are configuration fields.
- Resume may reprocess the final uncommitted batch but may never skip an ordinal.

## Configuration Fingerprint

Construct a canonical configuration document containing at least:

- schema and solver versions;
- source commit;
- puzzle slug, target, target script, network and path;
- image/mnemonic hashes;
- normalization lane and Unicode data/runtime version;
- candidate tier, source hashes, generator/rule IDs and ordering;
- filter and dedup semantics;
- exact N, shard layout and batch size;
- oracle/deriver implementation and dependency versions;
- witness specification;
- maximum-candidate limit.

Serialize as UTF-8 canonical JSON with sorted keys, fixed separators, no NaN/infinity and
explicit integer/string types. The configuration fingerprint is SHA-256 of those bytes.
Runtime-only facts such as current time, PID and host name do not belong in the fingerprint.

## Checkpoint Model

Use versioned JSON with these minimum fields:

```text
checkpoint_schema
solver_version
git_commit
config_fingerprint
search_strategy
tier
normalization_lane
source_hashes
shards[{start,end,next_ordinal,tested,status}]
generated_candidates
duplicates_removed
prior_candidates_removed
derived_candidates
started_at
updated_at
elapsed_monotonic_seconds
witness_status
rolling_identifier_digest
```

The checkpoint stores no plaintext candidate, passphrase, seed or private key. Write a
new file in the same directory, flush and `fsync` it, atomically replace the current file,
then `fsync` the directory. Retain one validated previous generation for recovery.

On startup, validate JSON/schema, configuration fingerprint, source hashes, ordinal
bounds, monotonic counters and shard non-overlap. A corrupt newest checkpoint may fall
back only to a validated prior generation and must report the rollback. A mismatch stops
with `CHECKPOINT_MISMATCH`; it never starts from zero silently.

## Candidate Tiers

No tier is executable until its exact source manifest, rules, N and prior-coverage
subtraction are available.

| Tier | Concept | Evidence | Expected size | Confidence/risk | Gate |
|---|---|---|---:|---|---|
| Tier 1 | Exact phrases/tokens explicitly present in primary puzzle materials and not proven previously tested | Direct | `UNKNOWN` until manifest | Highest relative confidence; still no direct passphrase hint | Recover exact old coverage first |
| Tier 2 | Small, separately counted case/separator/punctuation variants of Tier 1 | Direct token + weak mutation | `UNKNOWN` | Moderate false-prior risk | Each rule versioned and bounded |
| Tier 3 | Three-word combinations from recovered 35-token thematic corpus | Multiple thematic clues | 257,250 or 1,543,500 raw | Hypothesis; style semantics unresolved | Recover corpus and define grammar |
| Tier 4 | Broader author vocabulary/templates, potentially 108-token combinations | Author-context inference | 7,558,272 or 45,349,632 raw for named models | Lower confidence | Must satisfy two-hour rule after measured D |
| Tier 5 | Finite mask/probabilistic/exhaustive region | Weak hypothesis | Must be stated exactly | Highest risk and cost | Separate human GO decision required |

The contact-the-author lead is a pre-search information action, not a candidate tier. A
reply that constrains length, language, source or grammar requires recalculating all tiers.

## Stop Conditions

| Condition | Required behavior |
|---|---|
| `MATCH` | Stop scheduling, cancel/drain workers, preserve candidate privately in memory, run independent verification |
| `VERIFIED_MATCH` | Stop permanently and hand the result privately to the human; take no external action |
| `FALSE_MATCH` | Treat as critical derivation disagreement; preserve redacted diagnostics and stop |
| `EXHAUSTED` | Only when exact deduplicated N is processed, all shards complete and all witnesses pass |
| `INVALID_CONFIGURATION` | Stop before derivation; explain invalid field |
| `CHECKPOINT_MISMATCH` | Refuse resume; never silently reset or reinterpret |
| `CORRUPT_CHECKPOINT` | Attempt only validated previous generation; otherwise stop |
| `DERIVATION_ERROR` | Stop affected run; never count candidate as a negative |
| `WORKER_FAILURE` | Stop or deterministically reschedule uncommitted batch; never create a coverage gap |
| `WITNESS_FAILURE` | Mark run uncertified and stop |
| `BENCHMARK_FAILURE` | No search permission; return to implementation/validation |
| `MAX_CANDIDATES_REACHED` | Checkpoint and stop cleanly; do not advance to another tier |
| `ESCROW_NOT_FUNDED` | Stop before a real search |

No stop condition automatically launches another strategy or tier.

## Match Verification Procedure

1. An optimized worker reports a tentative match without writing plaintext to normal logs.
2. The scheduler immediately stops issuing work and preserves the candidate locally.
3. Reference Oracle A derives it again in the correct normalization lane.
4. Independent Oracle B derives it from the original candidate independently.
5. Compare seed hash, master fingerprint, child public key, HASH160 and address.
6. Decode the result and require the exact target witness program and full published
   address.
7. Require two `MATCH` results and identical intermediates; otherwise classify
   `FALSE_MATCH`/`DERIVATION_ERROR` and stop.
8. Store any confirmed candidate only in a permission-restricted local result outside
   repository/log/checkpoint paths.
9. Notify the human privately. Do not query other wallets, sign, broadcast or announce.

## Security Boundary

- This work applies only to
  `2-mid-prizes/corey-phillips-kitten-passphrase-1msats/`.
- The only verification target is the address intentionally published by the creator.
- All derivation and comparison are local.
- The verifier does not accept arbitrary addresses in normal operation.
- No unrelated wallet discovery, balance-based scanning, private-data collection or
  arbitrary key search is permitted.
- No transaction construction, signing or broadcasting is part of the system.
- A live escrow lookup is allowed only before a run to decide whether the public reward
  remains available; it is never performed per candidate.
- Secrets discovered during the game are not printed to normal logs or committed.

## Assumptions Register

| ID | Assumption | Evidence | Confidence | Impact if wrong | How to verify |
|---|---|---|---|---|---|
| A001 | The archived JPEG is the exact target-generating artifact | Hash matches manifest and author's published entropy | High | Entire mnemonic wrong | Fetch primary artifact and compare hashes |
| A002 | Base64 contains only JPEG bytes, no data-URI prefix | Reproduced author's entropy | High | Entropy/mnemonic wrong | Compare exact author digest and implementation |
| A003 | The public 24-word mnemonic is exact | Reproduced from entropy | High | Every derivation wrong | Independent BIP39 implementation |
| A004 | The primary path is `m/84'/0'/0'/0/0` | Published mechanism and oracle | High | Correct passphrase derives elsewhere | Pin/reproduce author's original code |
| A005 | The only primary unknown is the passphrase | Fixed image, mnemonic and path; author statement | High | Candidate-only oracle cannot solve | Audit primary code/article |
| A006 | The author's library applied BIP39 NFKD | Protocol expectation, not exact version proof | Medium | Non-ASCII candidates derive differently | Run exact 2019 dependency/version |
| A007 | Current raw-UTF-8 oracle negatives covered ASCII or intended bytes | Candidate artifacts absent | Low/unknown | Historical coverage may not transfer | Recover run manifests and engine config |
| A008 | Reported negative-run counts are accurate | Ledger and CSV agree arithmetically | Medium | Coverage overstated | Recover original logs/manifests |
| A009 | Reported cumulative count represents unique candidates | Cross-check row overlaps; no dedup artifacts | Low | Unique coverage overstated | Rebuild exact normalized candidate set |
| A010 | The image has no passphrase-bearing steganography | Historical tool reports only | Medium | Missed high-value clue | Reproduce documented stego analysis if justified |
| A011 | No additional public author clue exists | Historical source review | Medium | Search tiers miss strong constraint | Repeat source audit/contact author |
| A012 | The author chose a human-memorable passphrase | No confirmed clue; “not meant to be solved” cuts against it | Low | Thematic search has negligible probability | Ask author for one constraint |
| A013 | The target remains funded when searching | Dated snapshot only | Unknown/current | Compute spent on unavailable prize | Fresh on-chain check before run |
| A014 | Existing self-test certifies the full pipeline | It checks only hard-coded mnemonic to sister address | Low | False confidence in image/Unicode stages | Replace with layered independent vectors |

## Open Questions

| Priority | Question | Why it matters |
|---|---|---|
| `BLOCKER` | What exact 2019 `bip39`, `bip32` and address-library versions generated the target? | Resolves Unicode and author-compatibility semantics |
| `BLOCKER` | Can the original 35/108-token corpora, rule versions and per-run candidate manifests be recovered? | Required for exact deduplication and certified new negatives |
| `BLOCKER` | Can a second independent implementation reproduce every empty-passphrase intermediate? | Required before marking the new oracle verified |
| `IMPORTANT` | Was historical candidate normalization raw, NFKD, or engine-specific? | Determines whether prior non-ASCII coverage transfers |
| `IMPORTANT` | Is 1,155,064,682 a count of attempts rather than unique normalized candidates? | Changes coverage claims and subtraction |
| `IMPORTANT` | What precisely are the six three-word style semantics? | Required to define N and deterministic order |
| `IMPORTANT` | Does fresh chain state still show the target funded and unspent? | Required before any real run |
| `OPTIONAL` | Should path-mismatch tests derive 44'/49' keys but encode P2WPKH? | Clarifies a low-priority lead |
| `OPTIONAL` | Can the historical steganography and source-audit negatives be independently reproduced? | Improves confidence but is not needed to implement the oracle |

## Phase Gate

### Oracle implementation readiness: `GO`

The fixed target, primary path, known mnemonic, candidate variable, exact comparison and
independent-validation design are sufficiently specified to implement a minimal oracle.
Implementation must include the standards NFKD lane, explicitly isolate raw compatibility,
recompute the image/mnemonic in self-test, and expose no enumeration.

### Oracle verification status: `NO-GO`

The current oracle is not yet independently verified across all layers. The missing work
is the second implementation, official protocol vectors, Unicode equivalence tests and
comparison of the puzzle-specific intermediate values.

### Solver/search readiness: `NO-GO`

No production search should be implemented or run from this phase alone. Exact prior
candidate manifests are missing, normalization history is unresolved, candidate tiers are
not executable manifests, and no independently verified new oracle exists yet.

## Final Status

```text
Solver specification: COMPLETE
Oracle implementation readiness: GO
Oracle verification: NO-GO
Confirmed target: bc1qcyrndzgy036f6ax370g8zyvlw86ulawgt0246r
Unknown variables: BIP39 passphrase P; exact 2019 Unicode semantics M for non-ASCII
Derivation status: primary pipeline confirmed; full independent validation pending
Naive search space: unbounded
Evidence-constrained search space: unbounded
Hypothesis regions: 257,250 to 45,349,632 raw candidates for named three-word models
Blockers: exact old candidate manifests; exact 2019 dependency semantics; independent oracle validation
File created: research/corey/solver-spec.md
```

I do not advance automatically to oracle implementation. This phase ends for human review.
