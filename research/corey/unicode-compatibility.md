# Corey Phillips puzzle: Unicode compatibility note

## Status

The standards path is fixed: BIP39 NFKD normalization is mandatory for both
the mnemonic sentence and the passphrase before UTF-8 encoding and
PBKDF2-HMAC-SHA512.

The historical-compatibility question is unresolved. The original repository
linked by the puzzle author is no longer available at its published location.
A public mirror preserves the README, but no `package.json`, lockfile, or
readable source manifest was found there. The puzzle repository names the
historical JavaScript components (`bip39`, `bip32`, and `bitcoinjs-lib`) but
does not establish exact versions or the behavior of the deployed 2019 page.
It is therefore not defensible to assert whether that page normalized Unicode
before deriving the seed.

## Required behavior

`tools/corey_oracle.py` exposes two deliberately separate modes:

| Mode | Mnemonic | Passphrase | Status |
|---|---|---|---|
| `standard` | NFKD, then UTF-8 | NFKD, then UTF-8 | Normative default |
| `raw-compat` | UTF-8 as supplied | UTF-8 as supplied | Unverified historical hypothesis |

The compatibility mode is never selected automatically. It has no effect on
ASCII input because NFKD leaves ASCII unchanged. Its only purpose is to make a
future, evidence-backed compatibility check possible without weakening the
standard path.

The oracle does not trim whitespace, fold case, remove punctuation, or apply
language-specific transformations in either mode. NFKD decomposition is not
candidate canonicalization beyond the exact BIP39 requirement.

## Synthetic test matrix

No real puzzle candidates were tested during this investigation. The tests use
the synthetic pair `é` and `e` followed by U+0301:

- `standard` must produce identical seeds for the canonically equivalent pair;
- `raw-compat` must produce different seeds, demonstrating that the modes are
  isolated;
- leading spaces and case changes must remain significant.

The official BIP39 `TREZOR` vector independently checks the PBKDF2 result.

## Decision rule for future work

Do not use `raw-compat` in a real search unless primary evidence identifies the
deployed dependency version or archived source and a reproducible test proves
its byte-level behavior. Until then, any non-ASCII candidate result under that
mode is a compatibility hypothesis, not an oracle verdict suitable for search.

