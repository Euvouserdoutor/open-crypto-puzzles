# Corey Phillips kitten passphrase: attack plan

Scope: the intentionally published 2019 puzzle at
`2-mid-prizes/corey-phillips-kitten-passphrase-1msats/`. This plan does not scan
unrelated wallets, does not broadcast transactions, and does not begin a real candidate
sweep.

## Reverse-engineered state

| Item | Established value |
|---|---|
| Image | `clues/kitten.jpeg`, SHA-256 `b988e0881a0211222e83f3e2a4bfac695c951bf96aa33ec112fab6992f5e7343` |
| Image transform | SHA-256 of the RFC 4648 base64 encoding of the exact JPEG bytes |
| Entropy | `1808d35318ac7cb98b69ff9779b699d6a631f15e0b353ac89b7c4020774832ed` |
| Mnemonic | `blossom educate state course sick fresh color divide number soap please pull glide weather join grit depart dynamic tenant leopard alter piano slight room` |
| Unknown | BIP39 passphrase only |
| Path | `m/84'/0'/0'/0/0` on Bitcoin mainnet |
| Target | `bc1qcyrndzgy036f6ax370g8zyvlw86ulawgt0246r` |
| Calibration address | `bc1q57euh23y3qs2f9d5mtwpax5lqecfvrdkqce82a`, produced by the empty passphrase |
| Deterministic checker | `tools/oracle.py`; exact target-address comparison, with `--selftest` and streaming modes |

The passphrase is sometimes called the “25th word,” but that is only wallet terminology.
It is not constrained to one word or to the BIP39 wordlist. It is an independent string
mixed into seed generation; case, spaces and punctuation matter. Under BIP39, both the
mnemonic and passphrase are Unicode NFKD-normalized before UTF-8 encoding.

There is one compatibility issue to resolve before testing non-ASCII candidates:
`tools/oracle.py` currently encodes the passphrase directly and does not apply NFKD.
The empty-passphrase self-test cannot detect that difference. ASCII candidates are
unaffected. The author's JavaScript `bip39.mnemonicToSeed` route is expected to follow
BIP39 normalization, so the standards-compliant lane should be authoritative and the
current raw-Unicode behavior should be retained only as an explicitly labeled
compatibility lane until checked against the exact library version used in 2019.

## 1. Exact cryptographic derivation

1. Read the exact JPEG bytes `F` and compute `B = base64(F)`, without a data-URI prefix,
   line wrapping or trailing newline.
2. Compute `E = SHA256(B)`. Here `E` is the 32-byte value shown above.
3. Run BIP39 `entropyToMnemonic(E)`. For 256 bits of entropy, append the first 8 checksum
   bits of `SHA256(E)`, split the resulting 264 bits into 24 groups of 11 bits, and map
   them through the English BIP39 list. This produces the fixed mnemonic shown above.
4. For candidate passphrase `P`, calculate the 64-byte BIP39 seed:

   ```text
   password = UTF8(NFKD(mnemonic))
   salt     = UTF8("mnemonic" || NFKD(P))
   seed     = PBKDF2-HMAC-SHA512(password, salt, iterations=2048, dkLen=64)
   ```

5. Calculate the BIP32 master node:

   ```text
   I  = HMAC-SHA512(key="Bitcoin seed", data=seed)
   k0 = parse256(I[0:32])
   c0 = I[32:64]
   ```

6. Apply private-child derivation at indices `84'`, `0'`, `0'`, `0`, `0`. Hardened
   steps use `0x00 || ser256(k_parent) || ser32(index)`; non-hardened steps use the
   compressed parent public key followed by `ser32(index)`. For each step, HMAC-SHA512
   is keyed by the parent chain code, the left half is added to the parent private scalar
   modulo the secp256k1 order, and the right half becomes the child chain code. A final
   solver must also implement BIP32's negligible-probability invalid-child rules
   (`IL >= n` or child scalar zero), which the present oracle does not explicitly check.
7. Serialize the final secp256k1 public key in compressed form, compute
   `RIPEMD160(SHA256(pubkey))`, encode it as SegWit v0 P2WPKH with mainnet HRP `bc` and
   BIP173 Bech32, and compare the resulting address byte-for-byte with the target.

This is a deterministic local oracle. A candidate is a solution only if the final address
is exactly the published target.

## 2. Assumptions

1. The target remains funded and unspent when a future search starts. The repository's
   last exact accounting is 1,001,900 sats funded and zero spent on 2026-08-16; the
   address must be checked again immediately before every run.
2. The target was generated from the exact archived JPEG bytes. The image-to-mnemonic
   hash and empty-passphrase sister address strongly certify this.
3. The author used `m/84'/0'/0'/0/0`, as stated in the published code, rather than merely
   using a BIP84-shaped address with a key from another path.
4. The unknown is only the passphrase; there is no unknown mnemonic word, account,
   change or address index in the primary model.
5. The author may have chosen an arbitrary high-entropy secret. His statement that the
   puzzle “is not meant to be solved” means a human-memorable passphrase is only a
   hypothesis, not an established clue.
6. The steganography, missing-article and audio-puzzle channels recorded in the folder
   are genuine negatives.
7. The 1,155,064,682 recorded negatives are useful evidence but not formally exhaustive:
   the witness position was not logged per run, and the actual candidate files/run logs
   are absent from this repository.

## Clues and tested coverage

The confirmed passphrase clues are weak: the context is a kitten/photo, the author's
`bitimage` proof of concept, BIP39/BIP84, Bitcoin, and the author's public vocabulary.
The community hint repository points to generic wordlists and steganography, but supplies
no confirmed length, grammar, character set or source for the passphrase. The separate
audio puzzle establishes a related format, not a reusable secret.

Previously tested families, which must not be repeated, are:

| Family | Recorded candidates | Generation rule recorded in this folder |
|---|---:|---|
| Author-bundled SkullSecurity lists | 705,613 | raw words |
| `rockyou.txt` | 14,343,467 | raw entries |
| `rockyou` + best64 | 1,104,459,484 | best64 mutations |
| Corey-specific corpus | 23,735,781 | 108 mined words, raw plus best64, leetspeak, T0XlC, toggles3, rockyou-30000, OneRuleToRuleThemAll, d3ad0ne and dive |
| Corey in-jokes | 2,808,334 | raw plus best64 and OneRuleToRuleThemAll |
| Two-word thematic combinations | 7,350 | 35 words, ordered pairs, six styles: concatenated, space, underscore, dash, camelCase, PascalCase |
| Human-password lists | 8,967,534 | probable-v2-top12000, darkweb2017-top10k, xato-top-1M and ncsc-100k, raw and best64 |
| Quotes and BIP39 words | 29,201 | famous quotes plus each BIP39 word as a single passphrase |
| Audio message | 32 | case, punctuation, spacing and spelled-out-path variants |
| Alternate BIP84 index paths | 432 | Corey corpus at `0/1`, `1/0`, `1'/0/0` and `0/2` variants |
| Independent second implementation | 7,454 | subset cross-check; overlaps other families and is included in the repository's stated cumulative total |

The exact 35-word list, 108-word list, in-joke list, quotes, rules, generated candidates
and referenced `results/PASSPHRASE_RUNS.md`/`results/STATUS.md` are not present here.
Therefore the documented generators cannot yet be reproduced exactly and exact
deduplication against the old 1.155-billion-candidate history is impossible from this
checkout alone. Recovering hashes/manifests or regenerating the old sets deterministically
is a prerequisite to any new real sweep.

## 3. Search-space model

There is no finite global passphrase space. For illustration, all eight-character strings
over 95 printable ASCII symbols already contain `95^8 = 6,634,204,312,890,625`
candidates; blind enumeration is unjustified.

The useful model is a sequence of bounded, evidence-weighted regions:

| Region | Exact model | Raw N | At 343/s | At 12,700/s |
|---|---:|---:|---:|---:|
| Three thematic words, one style for the whole phrase | `35^3 * 6` | 257,250 | 12.5 min | 20 s |
| Three thematic words, independently chosen boundary styles | `35^3 * 6^2` | 1,543,500 | 75 min | 2.0 min |
| Three Corey words, one style | `108^3 * 6` | 7,558,272 | 6.1 h | 9.9 min |
| Three Corey words, independent boundary styles | `108^3 * 6^2` | 45,349,632 | 36.7 h | 59.5 min |

These formulas assume ordered selection with replacement. Actual unique counts will be
lower because concatenation/casing rules can collide. The folder's “hours” label for the
35-word three-word lead is inconsistent with its own documented rates: even the larger
independent-boundary interpretation is about two minutes at the recorded optimized CPU
rate. Its exact rule must be specified before running it.

Any numeric suffix family must be modeled explicitly. For example, appending every value
from `0000` through `9999` multiplies N by 10,000 and is not a harmless mutation. No
region above two hours at the measured engine rate should run until a new constraint
shrinks it.

## 4. Candidate-generation strategies

Ranked in the order I would pursue them:

1. **Acquire information, not compute.** Ask the author for one narrowing fact: whether
   the passphrase is one word or a phrase, approximate length, language, theme, or whether
   it appeared in public. This has the highest chance of changing the problem.
2. **Recover the missing candidate manifests.** Obtain the exact 35/108-word corpora,
   in-joke phrases, rule versions, per-run counts and preferably sorted candidate hashes.
   Without these, the repository cannot enforce its own “do not repeat” rule exactly.
3. **Audit the small documented gap.** Define three-word thematic generation precisely,
   first with one whole-phrase style, then with independent separators only if justified.
   Preserve word order and repetitions unless a linguistic constraint removes them.
4. **Phrase templates grounded in the author's text.** Generate grammatical templates
   from confirmed concepts rather than arbitrary Cartesian products. Each template must
   publish its token inventory, slots, casing, separators, punctuation and exact N before
   execution, and must be subtracted from prior sets.
5. **Date/project mutations only when evidenced.** Years, article dates, handles and
   project names may be combined with a base phrase only as separately budgeted regions.
   Avoid open-ended digit and symbol masks.
6. **Probabilistic models last.** A PCFG or language-model-ranked stream may prioritize
   plausible passphrases, but it is not exhaustive and must have a fixed candidate budget,
   deterministic model/version, stable ordering and exact deduplication. Generic password
   distributions have already received over a billion trials.

The proposed BIP44/BIP49 “safety net” needs precise semantics. A standard BIP44 address
is P2PKH and a standard BIP49 address is P2SH-P2WPKH, so neither textual address can equal
the Bech32 target. A meaningful test would derive keys at `m/44'/0'/0'/0/0` and
`m/49'/0'/0'/0/0` but still encode those public keys as P2WPKH. That tests an
author-path mismatch, not standard BIP44/BIP49 addresses. It is cheap but has a very low
prior because the published code states the exact BIP84 path.

## 5. Validation procedure

Before a run:

1. Confirm the target's funded/unspent state through `tools/check_escrows.py`.
2. Pin dependency versions and record the host, source revision and configuration.
3. Run `tools/oracle.py --selftest`; require the exact sister address and exit code 0.
4. Add standards vectors that compare raw and NFKD-equivalent Unicode passphrases against
   an independent BIP39/BIP32 implementation. Do not search non-ASCII candidates until
   this is resolved.
5. Generate three planted witnesses placed deterministically near the beginning, middle
   and end of every shard. Each must traverse the same generator, normalization,
   derivation and comparison path as real candidates.
6. Compute N before the run, benchmark D on synthetic strings, and calculate `t = N/D`.
7. For each candidate, derive locally and compare only with the published target. Do not
   query a blockchain explorer per candidate.
8. On an apparent match, stop all workers, reproduce it with the certified oracle and a
   second independent implementation, and give the passphrase privately to the human.
   Never broadcast automatically or commit secret material.
9. A negative is certified only if processed count equals the deduplicated planned N,
   every shard completed, and all head/middle/tail witnesses were recovered.

On 2026-08-19 I re-ran the existing self-test using a temporary API-compatible secp256k1
adapter backed by the installed `cryptography` library because the declared `ecdsa`
package was unavailable in the environment. It reproduced the sister address exactly
and produced the documented negative-control address. This did not test any real
passphrase candidate.

## 6. Estimated CPU rate

A 500-item synthetic, single-process run through the full current Python oracle measured
approximately **343 candidates/s** on the present host. PBKDF2 alone measured about
**1,094 candidates/s**, confirming that PBKDF2-HMAC-SHA512 plus repeated Python-level
secp256k1 derivation is the bottleneck. These are planning measurements, not a real
search.

The historical ledger reports **12,700 candidates/s on an optimized CPU engine** and
**1,000/s with btcrecover**. Planning should therefore use two CPU figures:

- 300–400/s for the current single-process Python oracle;
- 10,000–12,700/s only after the new solver reproduces that rate on the intended host
  with full validation and witnesses.

## 7. GPU acceleration

GPU acceleration materially helps only after the candidate region is large enough to
amortize setup and transfer costs. The recorded GPU rates are 315,000/s for one raw run
and 690,000/s for rule-heavy runs: roughly 25–55 times the recorded optimized CPU engine
and about 900–2,000 times this single-process Python oracle.

For the 257,250- to 1,543,500-candidate thematic regions, optimized CPU execution should
finish in seconds to about two minutes, so GPU rental is unnecessary. For tens of
millions of candidates, GPU becomes useful; for hundreds of millions or billions, it is
material. GPU speed does not repair a weak hypothesis, missing deduplication data or an
uncertified negative.

## 8. Checkpoint/resume strategy

Every run should have an immutable run manifest containing:

- puzzle slug, target and source commit;
- oracle/engine version and normalization lane;
- generator ID and version;
- SHA-256 hashes of every corpus and rule file;
- formula and exact deduplicated N;
- shard count and deterministic ordinal ranges;
- next unprocessed ordinal per shard;
- tested count, elapsed time and measured rate;
- rolling digest of candidate identifiers;
- witness identifiers and recovery status;
- start/update/completion timestamps.

Checkpoint after a fixed number of candidates or at most every 60 seconds. Write a new
checkpoint, flush it, then atomically rename it over the previous checkpoint. Resume only
when all hashes and configuration values match. Reprocess at most the last incomplete
batch; deduplication makes that harmless. Never checkpoint a discovered passphrase into
the repository.

## 9. Deduplication strategy

1. Define candidate identity as the exact seed-effective byte string: NFKD-normalized
   UTF-8 in the standards lane, raw UTF-8 only in the labeled compatibility lane.
2. Canonicalize line endings only at corpus ingestion; do not trim meaningful leading or
   trailing spaces from generated passphrases.
3. Use an exact disk-backed unique set keyed by candidate bytes, or generate disjoint
   canonical ordinal ranges whose uniqueness is proven. Do not rely on a Bloom filter:
   false positives could skip the solution.
4. Store a mapping from unique candidate ID to deterministic generator coordinates so a
   match can be reconstructed without logging all plaintext candidates.
5. Build a prior-coverage set from recovered old manifests and subtract it before
   deriving addresses. Until that set exists, label overlap estimates as unknown and do
   not claim a new exhaustive negative.
6. Report generated count, duplicate count, prior-covered count and actually derived
   count separately.

## 10. Safest first experiment

The safest first experiment is **not a passphrase search**:

1. restore the declared dependencies in an isolated environment;
2. run the existing empty-passphrase self-test;
3. add independent BIP39/BIP32 test vectors, including Unicode NFKD equivalence;
4. implement head/middle/tail planted witnesses and atomic checkpoint/resume;
5. benchmark a fixed synthetic corpus that contains no puzzle-derived candidates;
6. verify deterministic counts and identical results after an interrupted/resumed run.

Only after that harness passes should the first real bounded experiment be chosen. The
preferred first real region is the precisely defined 35-word three-word thematic set,
but it must wait until the missing 35-word corpus and old-candidate coverage are recovered
so no previous candidate is repeated. The alternate-path check is smaller, but its exact
P2WPKH-from-BIP44/BIP49-path interpretation must be documented first.

## Decision

The cryptographic side is completely deterministic and locally verifiable; the
passphrase side is underconstrained. The best next gain comes from recovering missing run
manifests or obtaining one new clue from the author, not from expanding generic brute
force. No large search should start from the current repository state.
