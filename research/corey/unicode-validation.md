# Corey Phillips puzzle: Unicode differential validation

## Result

NFKD cross-validation passed between CPython 3.12.13 (`unicodedata` 15.0.0)
and Node.js 24.19.0 (`String.normalize`, ICU 78.3 / Unicode 17.0). Both
implementations normalize the mnemonic and passphrase separately, encode the
results as UTF-8, construct the salt as `b"mnemonic" + normalized_passphrase`,
and run PBKDF2-HMAC-SHA512 with 2,048 iterations and a 64-byte output.

The corpus is explicit and deterministic: 15 synthetic values, zero real
puzzle candidates. Case, punctuation and whitespace are never trimmed,
collapsed or folded.

## Byte-level matrix

`raw UTF-8` is hexadecimal. Seed columns are the first 16 hexadecimal digits of
SHA256(seed), sufficient as a safe comparison fingerprint; formal BIP39 tests
compare the complete published seed internally.

| # | Raw UTF-8 | Raw code points | NFKD code points | Seed fp A | Seed fp B | Result |
|---:|---|---|---|---|---|---|
| 1 | `∅` | `∅` | `∅` | `d93411b7863f34d2` | `d93411b7863f34d2` | PASS |
| 2 | `6b697474656e` | `U+006B U+0069 U+0074 U+0074 U+0065 U+006E` | same | `f62128bd1cd3bf59` | `f62128bd1cd3bf59` | PASS |
| 3 | `68656c6c6f20776f726c64` | `U+0068 U+0065 U+006C U+006C U+006F U+0020 U+0077 U+006F U+0072 U+006C U+0064` | same | `d7177ab2b673a74e` | `d7177ab2b673a74e` | PASS |
| 4 | `313233343536` | `U+0031 U+0032 U+0033 U+0034 U+0035 U+0036` | same | `5a470659656b9f56` | `5a470659656b9f56` | PASS |
| 5 | `636166c3a9` | `U+0063 U+0061 U+0066 U+00E9` | `U+0063 U+0061 U+0066 U+0065 U+0301` | `f767b5464ee5cfc9` | `f767b5464ee5cfc9` | PASS |
| 6 | `63616665cc81` | `U+0063 U+0061 U+0066 U+0065 U+0301` | same | `f767b5464ee5cfc9` | `f767b5464ee5cfc9` | PASS |
| 7 | `e291a0` | `U+2460` | `U+0031` | `71d7330714f73d1d` | `71d7330714f73d1d` | PASS |
| 8 | `efac81` | `U+FB01` | `U+0066 U+0069` | `a23e10e49809e72b` | `a23e10e49809e72b` | PASS |
| 9 | `65cc81cca3` | `U+0065 U+0301 U+0323` | `U+0065 U+0323 U+0301` | `e9450fa659233877` | `e9450fa659233877` | PASS |
| 10 | `e78cab` | `U+732B` | same | `fa7fb09aab1d2b68` | `fa7fb09aab1d2b68` | PASS |
| 11 | `20cea920` | `U+0020 U+03A9 U+0020` | same | `aa2a4a4a07db2e43` | `aa2a4a4a07db2e43` | PASS |
| 12 | `206c656164696e67` | `U+0020 U+006C U+0065 U+0061 U+0064 U+0069 U+006E U+0067` | same | `c06cd57afff0a217` | `c06cd57afff0a217` | PASS |
| 13 | `747261696c696e6720` | `U+0074 U+0072 U+0061 U+0069 U+006C U+0069 U+006E U+0067 U+0020` | same | `3350cb24fa81e85c` | `3350cb24fa81e85c` | PASS |
| 14 | `74776f2020737061636573` | `U+0074 U+0077 U+006F U+0020 U+0020 U+0073 U+0070 U+0061 U+0063 U+0065 U+0073` | same | `d5c0e1beb523d6fa` | `d5c0e1beb523d6fa` | PASS |
| 15 | `6e6fc2a0627265616b` | `U+006E U+006F U+00A0 U+0062 U+0072 U+0065 U+0061 U+006B` | `U+006E U+006F U+0020 U+0062 U+0072 U+0065 U+0061 U+006B` | `140cd2bd990ff658` | `140cd2bd990ff658` | PASS |

The composed and decomposed Latin entries converge under NFKD. The circled
digit, ligature and non-breaking space demonstrate compatibility decomposition.
Combining marks demonstrate canonical reordering. Leading, trailing and repeated
ordinary spaces remain significant.

## Historical 2019 behavior

The author's public `index.html` loads committed browser bundles and calls:

```text
bip39.mnemonicToSeed(mnemonic, passphrase)
```

The exact committed `bip39.min.js` applies `.normalize('NFKD')` to both values
before UTF-8 encoding. It was introduced with the BIP32 bundle in commit
`560b2a2f048c61a825f04e97412389a69d71159d` on 2019-05-11. The same commit
identifies `bitcoinjs-lib` 5.0.3, but does not record exact npm versions for the
BIP39 or BIP32 bundles.

The original BIP39 bundle was executed directly on six controlled inputs:
empty, ASCII, composed/decomposed Latin, a compatibility character and a
non-breaking-space case. Every 64-byte seed equaled the standards derivation.

Classification: `HISTORICAL_BEHAVIOR_VERIFIED`.

Sources: the author's public
[`index.html`](https://github.com/coreyphillips/bitimage/blob/master/index.html),
[`bip39.min.js`](https://github.com/coreyphillips/bitimage/blob/master/bip39.min.js),
and repository history. No legacy bundle was copied into this repository.

