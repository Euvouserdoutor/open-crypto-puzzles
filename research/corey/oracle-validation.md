# Corey Phillips puzzle: independent oracle validation

## Outcome

Implementation A and the independently written JavaScript Implementation B
agree at every observable stage for the fixed 15-value synthetic Unicode corpus,
controlled path mutations and neighboring-input tests. Both independently pass
published protocol vectors. No divergence was found.

Real candidate enumeration: **0**. Real brute force: **NO**.

## Validation matrix

| Layer | Protocol vector | Implementation A | Implementation B | Agreement | Status |
|---|---|---|---|---|---|
| Unicode/NFKD | Canonically equivalent and compatibility-character controls | Python Unicode 15.0 | ICU Unicode 17.0 | Yes, 15/15 | VERIFIED |
| BIP39 | Official `abandon ... about` + `TREZOR` full seed | Pass | Pass | Yes | VERIFIED |
| PBKDF2 | SHA512, 2,048 iterations, 64 bytes, exact salt | Pass | Pass | Yes | VERIFIED |
| BIP32 | Official vector 1 master, `m/0'`, `m/0'/1` | Pass | Pass | Yes | VERIFIED |
| secp256k1 | Scalar 1 compressed generator | Pure Python pass | OpenSSL ECDH pass | Yes | VERIFIED |
| HASH160 | Cross-pipeline public-key payloads | Pass | Pass | Yes | VERIFIED |
| P2WPKH | 20-byte witness-v0 program | Pass | Pass | Yes | VERIFIED |
| Bech32 | BIP173 valid address plus invalid checksum tests | Pass | Pass | Yes | VERIFIED |
| Target decoding | Published target | `bc`, v0, 20 bytes | `bc`, v0, 20 bytes | Exact | VERIFIED |
| End-to-end synthetic | Fixed mnemonic, controlled passphrases, BIP84 path | Pass | Pass | Exact intermediates | VERIFIED |

The exact target program independently decoded by both paths is
`c1073689047c749d74d1f3d071119f71f5cff5c8`.

## Three verification levels

### Level 1 — Protocol correctness: VERIFIED

Full published BIP39 output, BIP32 hardened and non-hardened nodes, the
secp256k1 generator and BIP173 encoding/decoding all pass. Invalid Bech32 and
malformed path inputs fail closed.

### Level 2 — Pipeline correctness: VERIFIED

For each controlled input, the paths compare:

- normalized mnemonic byte hash;
- normalized passphrase bytes and byte hash;
- seed hash;
- master fingerprint;
- child-private-key hash;
- compressed public key;
- HASH160; and
- final address.

Case, whitespace and single-character mutations changed the derived result.
Changing the final derivation index and changing a normal step to hardened also
changed the result identically in A and B. A controlled synthetic target produced
`MATCH`; a one-character mutation produced `NO_MATCH`; malformed input produced
`ERROR`.

### Level 3 — Puzzle configuration correctness: VERIFIED

| Constant | Value | Primary evidence | Independently reconstructable? |
|---|---|---|---|
| Image SHA256 | `b988e088...5e7343` | Committed author-published JPEG | Yes, A and B |
| Entropy | `1808d353...4832ed` | Author's base64-then-SHA256 mechanism | Yes, A and B |
| Mnemonic | 24 English words beginning `blossom educate` | Image entropy plus BIP39 English list | Yes; checksum indices reconstructed by A and B |
| Derivation path | `m/84'/0'/0'/0/0` | Original `index.html` and sister address | Yes; both reach the sister address with empty passphrase |
| Network | Bitcoin mainnet | Original code uses `Bitcoin.networks.bitcoin`; target HRP `bc` | Yes |
| Address type | Native P2WPKH | Original code calls `Bitcoin.payments.p2wpkh`; witness program is 20 bytes | Yes |
| Target | `bc1qcyrn...0246r` | Author's publication and repository README | Yes, checksum and structure decoded independently |

The original source resolves the last material configuration ambiguity: its
BIP39 bundle normalizes both mnemonic and passphrase with NFKD. The separate
`raw-compat` lane remains isolated for audit history but is not the historical
primary behavior.

## Historical dependency audit

The author repository contains vendor bundles rather than `package.json`,
`package-lock.json` or `yarn.lock`. Git history establishes:

- commit `560b2a2f048c61a825f04e97412389a69d71159d` added the BIP39 and BIP32
  bundles on 2019-05-11;
- that commit explicitly upgraded `bitcoinjs-lib` to 5.0.3;
- `index.html` calls `Bitcoin.crypto.sha256`, `bip39.entropyToMnemonic`,
  `bip39.mnemonicToSeed`, `bip32.fromSeed`, BIP84 `derivePath`, and
  `Bitcoin.payments.p2wpkh`;
- the exact BIP39 bundle directly shows NFKD for mnemonic and passphrase and
  PBKDF2-HMAC-SHA512 with 2,048 iterations and 64-byte output; and
- the exact npm release numbers of the BIP39 and BIP32 bundles remain unknown.

Therefore, dependency-version status is **PARTIAL**, while historical Unicode
behavior is **VERIFIED**. The immutable bundled source is stronger evidence for
behavior than a guessed package version would be.

## Independence and limitations

Overall independence is **MODERATE**, not strong. Python and JavaScript use
different Unicode engines, independent BIP32 orchestration, different
secp256k1 implementations and independent Bech32 code. Both runtimes link
OpenSSL 3.5.7 for PBKDF2 and HASH160 primitives. Published protocol vectors
reduce the risk created by that shared dependency, but the sharing is recorded
rather than hidden.

Unicode database versions differ. All controlled characters predate the puzzle
and agree byte-for-byte. A future candidate engine must preserve exact Unicode
input and continue to deduplicate by NFKD UTF-8 bytes.

## Test record

Commands:

```text
node tools/corey_oracle_b.js --selftest
python3 -m unittest -v tests/test_corey_oracle.py tests/test_corey_oracle_differential.py
```

Result: all six Implementation B self-test groups passed; all 21 Python and
differential tests passed. Corpus size was 15 explicit synthetic Unicode values.
No wordlist, historical attempt list, candidate generator, multiprocessing or
GPU code was loaded or created.

## Gate

- Oracle implementation: **VERIFIED**.
- Puzzle configuration: **VERIFIED**.
- Overall oracle: **VERIFIED**.
- Ready for Phase 6 candidate-generation engineering: **GO**, subject to human
  review and the Phase 5 hard stop. Phase 6 has not begun.

