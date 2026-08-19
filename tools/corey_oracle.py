#!/usr/bin/env python3
"""Single-candidate deterministic oracle for the Corey Phillips puzzle.

This module deliberately contains no candidate generator, input loop, wordlist
reader, multiprocessing, network access, or transaction functionality.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys
import unicodedata
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Sequence


TARGET_ADDRESS = "bc1qcyrndzgy036f6ax370g8zyvlw86ulawgt0246r"
TARGET_PROGRAM_HEX = "c1073689047c749d74d1f3d071119f71f5cff5c8"
DERIVATION_PATH = "m/84'/0'/0'/0/0"

PUZZLE_RELATIVE_IMAGE = Path(
    "2-mid-prizes/corey-phillips-kitten-passphrase-1msats/clues/kitten.jpeg"
)
EXPECTED_IMAGE_SHA256 = "b988e0881a0211222e83f3e2a4bfac695c951bf96aa33ec112fab6992f5e7343"
EXPECTED_ENTROPY_HEX = "1808d35318ac7cb98b69ff9779b699d6a631f15e0b353ac89b7c4020774832ed"
EXPECTED_WORD_INDICES = (
    192, 564, 1702, 394, 1598, 742, 365, 511, 1211, 1645, 1331, 1386,
    792, 1989, 961, 821, 470, 550, 1784, 1026, 59, 1312, 1629, 1503,
)
EXPECTED_WORDS = (
    "blossom", "educate", "state", "course", "sick", "fresh", "color",
    "divide", "number", "soap", "please", "pull", "glide", "weather",
    "join", "grit", "depart", "dynamic", "tenant", "leopard", "alter",
    "piano", "slight", "room",
)
EXPECTED_EMPTY_ADDRESS = "bc1q57euh23y3qs2f9d5mtwpax5lqecfvrdkqce82a"
EXPECTED_EMPTY_SEED_SHA256 = "d93411b7863f34d244eb36508e5ca56466ddffcdb66955d8121d273493124d80"
EXPECTED_EMPTY_MASTER_FINGERPRINT = "d7769df5"
EXPECTED_EMPTY_FINAL_PUBKEY = "021209b131dfbd1efcfe15b1d1e92002653f5fc98e9ff6cb73a0d70153dbe58463"
EXPECTED_EMPTY_HASH160 = "a7b3cbaa248820a495b4dadc1e9a9f0670960db6"

# secp256k1 domain parameters.
FIELD_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
CURVE_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GENERATOR = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)
BECH32_ALPHABET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


class OracleError(Exception):
    """Controlled derivation or validation failure."""


class OracleResult(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    ERROR = "ERROR"


class NormalizationMode(str, Enum):
    STANDARD = "standard"
    RAW_COMPAT = "raw-compat"


@dataclass(frozen=True)
class DerivationTrace:
    mode: str
    normalized_candidate_utf8_length: int
    candidate_sha256: str
    seed_sha256: str
    master_fingerprint: str
    final_pubkey: str
    hash160: str
    address: str


def normalize_bip39_text(value: str) -> str:
    """Apply the NFKD normalization required by BIP39."""
    if not isinstance(value, str):
        raise OracleError("BIP39 text must be a Unicode string")
    return unicodedata.normalize("NFKD", value)


def _encode_bip39_text(value: str, mode: str | NormalizationMode) -> bytes:
    try:
        selected = NormalizationMode(mode)
    except ValueError as exc:
        raise OracleError(f"unsupported normalization mode: {mode}") from exc
    if not isinstance(value, str):
        raise OracleError("BIP39 text must be a Unicode string")
    if selected is NormalizationMode.STANDARD:
        value = normalize_bip39_text(value)
    return value.encode("utf-8")


def bip39_seed(
    mnemonic: str,
    passphrase: str,
    mode: str | NormalizationMode = NormalizationMode.STANDARD,
) -> bytes:
    """Derive the 64-byte BIP39 seed; standard mode normalizes both inputs."""
    password = _encode_bip39_text(mnemonic, mode)
    salt = b"mnemonic" + _encode_bip39_text(passphrase, mode)
    return hashlib.pbkdf2_hmac("sha512", password, salt, 2048, dklen=64)


def image_entropy(image_path: Path) -> tuple[str, bytes]:
    """Return raw-file SHA256 and SHA256 of its exact RFC 4648 base64 bytes."""
    try:
        raw = image_path.read_bytes()
    except OSError as exc:
        raise OracleError(f"cannot read puzzle image: {exc}") from exc
    return hashlib.sha256(raw).hexdigest(), hashlib.sha256(base64.b64encode(raw)).digest()


def entropy_to_indices(entropy: bytes) -> tuple[int, ...]:
    """Convert valid BIP39 entropy to checksum-bearing 11-bit word indices."""
    if len(entropy) not in (16, 20, 24, 28, 32):
        raise OracleError("BIP39 entropy length must be 128..256 bits in 32-bit steps")
    checksum_bits = len(entropy) * 8 // 32
    payload = int.from_bytes(entropy, "big")
    checksum = hashlib.sha256(entropy).digest()[0] >> (8 - checksum_bits)
    combined = (payload << checksum_bits) | checksum
    count = (len(entropy) * 8 + checksum_bits) // 11
    return tuple((combined >> (11 * (count - 1 - i))) & 0x7FF for i in range(count))


def reconstruct_puzzle_mnemonic(image_path: Path) -> tuple[str, str, bytes]:
    """Reconstruct and validate the puzzle mnemonic from the image bytes.

    The repository intentionally does not duplicate the full BIP39 wordlist.
    Instead, the independently computed indices are checked against the 24
    official English-word indices required by this one puzzle.
    """
    raw_digest, entropy = image_entropy(image_path)
    indices = entropy_to_indices(entropy)
    if indices != EXPECTED_WORD_INDICES:
        raise OracleError("image-derived BIP39 indices differ from the puzzle fixture")
    return raw_digest, " ".join(EXPECTED_WORDS), entropy


def _point_add(left: tuple[int, int] | None, right: tuple[int, int] | None):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % FIELD_P == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1) * pow(2 * y1, FIELD_P - 2, FIELD_P) % FIELD_P
    else:
        slope = (y2 - y1) * pow((x2 - x1) % FIELD_P, FIELD_P - 2, FIELD_P) % FIELD_P
    x3 = (slope * slope - x1 - x2) % FIELD_P
    return x3, (slope * (x1 - x3) - y1) % FIELD_P


def _scalar_multiply(scalar: int, point=GENERATOR):
    if not 0 < scalar < CURVE_N:
        raise OracleError("invalid secp256k1 scalar")
    result = None
    addend = point
    while scalar:
        if scalar & 1:
            result = _point_add(result, addend)
        addend = _point_add(addend, addend)
        scalar >>= 1
    return result


def compressed_public_key(private_key: int) -> bytes:
    point = _scalar_multiply(private_key)
    if point is None:
        raise OracleError("point at infinity")
    x, y = point
    return bytes([2 | (y & 1)]) + x.to_bytes(32, "big")


def hash160(payload: bytes) -> bytes:
    try:
        return hashlib.new("ripemd160", hashlib.sha256(payload).digest()).digest()
    except ValueError as exc:
        raise OracleError("RIPEMD160 is unavailable in this Python runtime") from exc


def master_from_seed(seed: bytes) -> tuple[int, bytes]:
    digest = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key = int.from_bytes(digest[:32], "big")
    if not 0 < key < CURVE_N:
        raise OracleError("BIP32 produced an invalid master key")
    return key, digest[32:]


def ckd_private(parent_key: int, parent_chain: bytes, index: int) -> tuple[int, bytes]:
    if not 0 <= index <= 0xFFFFFFFF:
        raise OracleError("BIP32 child index out of range")
    if index >= 0x80000000:
        data = b"\x00" + parent_key.to_bytes(32, "big")
    else:
        data = compressed_public_key(parent_key)
    digest = hmac.new(parent_chain, data + index.to_bytes(4, "big"), hashlib.sha512).digest()
    left = int.from_bytes(digest[:32], "big")
    child = (left + parent_key) % CURVE_N
    if left >= CURVE_N or child == 0:
        raise OracleError("BIP32 invalid child; fixed path cannot be evaluated")
    return child, digest[32:]


def parse_derivation_path(path: str) -> tuple[int, ...]:
    parts = path.split("/")
    if not parts or parts[0] != "m":
        raise OracleError("derivation path must start with m")
    result = []
    for item in parts[1:]:
        hardened = item.endswith(("'", "h", "H"))
        number = item[:-1] if hardened else item
        if not number.isdecimal():
            raise OracleError(f"invalid derivation component: {item}")
        index = int(number)
        if index >= 0x80000000:
            raise OracleError("derivation component is too large")
        result.append(index | (0x80000000 if hardened else 0))
    return tuple(result)


def derive_private_path(seed: bytes, path: str = DERIVATION_PATH) -> tuple[int, bytes, int]:
    key, chain = master_from_seed(seed)
    master_key = key
    for index in parse_derivation_path(path):
        key, chain = ckd_private(key, chain, index)
    return key, chain, master_key


def _bech32_polymod(values: Iterable[int]) -> int:
    generators = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)
    checksum = 1
    for value in values:
        top = checksum >> 25
        checksum = ((checksum & 0x1FFFFFF) << 5) ^ value
        for bit, generator in enumerate(generators):
            if (top >> bit) & 1:
                checksum ^= generator
    return checksum


def _bech32_hrp_expand(hrp: str) -> list[int]:
    return [ord(char) >> 5 for char in hrp] + [0] + [ord(char) & 31 for char in hrp]


def _convert_bits(data: Iterable[int], from_bits: int, to_bits: int, pad: bool) -> list[int]:
    accumulator = 0
    bit_count = 0
    result = []
    max_value = (1 << to_bits) - 1
    for value in data:
        if value < 0 or value >> from_bits:
            raise OracleError("invalid value during bit conversion")
        accumulator = (accumulator << from_bits) | value
        bit_count += from_bits
        while bit_count >= to_bits:
            bit_count -= to_bits
            result.append((accumulator >> bit_count) & max_value)
    if pad:
        if bit_count:
            result.append((accumulator << (to_bits - bit_count)) & max_value)
    elif bit_count >= from_bits or ((accumulator << (to_bits - bit_count)) & max_value):
        raise OracleError("invalid Bech32 padding")
    return result


def encode_segwit_v0(program: bytes, hrp: str = "bc") -> str:
    if len(program) not in (20, 32):
        raise OracleError("witness v0 program must be 20 or 32 bytes")
    data = [0] + _convert_bits(program, 8, 5, True)
    values = _bech32_hrp_expand(hrp) + data + [0] * 6
    polymod = _bech32_polymod(values) ^ 1
    checksum = [(polymod >> (5 * (5 - i))) & 31 for i in range(6)]
    return hrp + "1" + "".join(BECH32_ALPHABET[value] for value in data + checksum)


def decode_segwit_address(address: str) -> tuple[str, int, bytes]:
    if not isinstance(address, str) or not 8 <= len(address) <= 90:
        raise OracleError("invalid Bech32 length")
    if address.lower() != address and address.upper() != address:
        raise OracleError("mixed-case Bech32 address")
    address = address.lower()
    separator = address.rfind("1")
    if separator < 1 or separator + 7 > len(address):
        raise OracleError("invalid Bech32 separator")
    hrp = address[:separator]
    try:
        data = [BECH32_ALPHABET.index(char) for char in address[separator + 1 :]]
    except ValueError as exc:
        raise OracleError("invalid Bech32 character") from exc
    if _bech32_polymod(_bech32_hrp_expand(hrp) + data) != 1:
        raise OracleError("invalid Bech32 checksum")
    payload = data[:-6]
    if not payload or payload[0] != 0:
        raise OracleError("oracle accepts only witness version 0")
    program = bytes(_convert_bits(payload[1:], 5, 8, False))
    if len(program) not in (20, 32):
        raise OracleError("invalid witness v0 program length")
    return hrp, 0, program


def derive_candidate(
    passphrase: str,
    mode: str | NormalizationMode = NormalizationMode.STANDARD,
    mnemonic: str = " ".join(EXPECTED_WORDS),
) -> DerivationTrace:
    encoded_candidate = _encode_bip39_text(passphrase, mode)
    seed = bip39_seed(mnemonic, passphrase, mode)
    child_key, _chain, master_key = derive_private_path(seed)
    public_key = compressed_public_key(child_key)
    program = hash160(public_key)
    address = encode_segwit_v0(program)
    return DerivationTrace(
        mode=NormalizationMode(mode).value,
        normalized_candidate_utf8_length=len(encoded_candidate),
        candidate_sha256=hashlib.sha256(encoded_candidate).hexdigest(),
        seed_sha256=hashlib.sha256(seed).hexdigest(),
        master_fingerprint=hash160(compressed_public_key(master_key))[:4].hex(),
        final_pubkey=public_key.hex(),
        hash160=program.hex(),
        address=address,
    )


def verify_candidate(passphrase: str, mode: str | NormalizationMode = NormalizationMode.STANDARD) -> OracleResult:
    try:
        trace = derive_candidate(passphrase, mode)
    except (OracleError, TypeError, ValueError):
        return OracleResult.ERROR
    return OracleResult.MATCH if trace.address == TARGET_ADDRESS else OracleResult.NO_MATCH


def _assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise OracleError(f"self-test failed: {label}")


def run_selftest(image_path: Path | None = None) -> dict[str, str]:
    """Run independent protocol vectors and puzzle reconstruction checks."""
    checks: dict[str, str] = {}

    # Official BIP39 vector: entropy 000...000, mnemonic abandon...about,
    # passphrase TREZOR. The expected seed is copied from the public vector,
    # not produced or stored by this puzzle.
    vector_mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    vector_seed = bip39_seed(vector_mnemonic, "TREZOR")
    _assert_equal(
        vector_seed.hex(),
        "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e5349553"
        "1f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04",
        "BIP39 seed vector",
    )
    _assert_equal(bip39_seed(vector_mnemonic, "é"), bip39_seed(vector_mnemonic, "e\u0301"), "BIP39 NFKD")
    if bip39_seed(vector_mnemonic, "é", NormalizationMode.RAW_COMPAT) == bip39_seed(
        vector_mnemonic, "e\u0301", NormalizationMode.RAW_COMPAT
    ):
        raise OracleError("self-test failed: raw compatibility isolation")
    checks["bip39_nfkd"] = "PASS"

    # Official BIP32 vector 1, seed 000102030405060708090a0b0c0d0e0f.
    vector_master, vector_chain = master_from_seed(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))
    _assert_equal(f"{vector_master:064x}", "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35", "BIP32 master private key")
    _assert_equal(vector_chain.hex(), "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508", "BIP32 master chain code")
    child, child_chain = ckd_private(vector_master, vector_chain, 0x80000000)
    _assert_equal(f"{child:064x}", "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea", "BIP32 m/0H private key")
    _assert_equal(child_chain.hex(), "47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141", "BIP32 m/0H chain code")
    checks["bip32"] = "PASS"

    _assert_equal(compressed_public_key(1).hex(), "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798", "secp256k1 generator")
    checks["secp256k1"] = "PASS"

    vector_program = bytes.fromhex("751e76e8199196d454941c45d1b3a323f1433bd6")
    vector_address = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
    _assert_equal(encode_segwit_v0(vector_program), vector_address, "BIP173 address vector")
    _assert_equal(decode_segwit_address(vector_address), ("bc", 0, vector_program), "BIP173 decode vector")
    checks["bech32_p2wpkh"] = "PASS"

    if image_path is None:
        image_path = Path(__file__).resolve().parents[1] / PUZZLE_RELATIVE_IMAGE
    raw_digest, mnemonic, entropy = reconstruct_puzzle_mnemonic(image_path)
    _assert_equal(raw_digest, EXPECTED_IMAGE_SHA256, "puzzle image SHA256")
    _assert_equal(entropy.hex(), EXPECTED_ENTROPY_HEX, "puzzle image entropy")
    empty_trace = derive_candidate("", mnemonic=mnemonic)
    _assert_equal(empty_trace.seed_sha256, EXPECTED_EMPTY_SEED_SHA256, "empty-passphrase seed digest")
    _assert_equal(empty_trace.master_fingerprint, EXPECTED_EMPTY_MASTER_FINGERPRINT, "empty-passphrase master fingerprint")
    _assert_equal(empty_trace.final_pubkey, EXPECTED_EMPTY_FINAL_PUBKEY, "empty-passphrase child public key")
    _assert_equal(empty_trace.hash160, EXPECTED_EMPTY_HASH160, "empty-passphrase HASH160")
    _assert_equal(empty_trace.address, EXPECTED_EMPTY_ADDRESS, "empty-passphrase sister address")
    checks["puzzle_reconstruction"] = "PASS"

    _assert_equal(decode_segwit_address(TARGET_ADDRESS), ("bc", 0, bytes.fromhex(TARGET_PROGRAM_HEX)), "target structure")
    checks["target_structure"] = "PASS"
    return checks


def _safe_debug(trace: DerivationTrace) -> str:
    return json.dumps(
        {
            "mode": trace.mode,
            "normalized_candidate_utf8_length": trace.normalized_candidate_utf8_length,
            "candidate_sha256": trace.candidate_sha256,
            "seed_sha256": trace.seed_sha256,
            "master_fingerprint": trace.master_fingerprint,
            "final_compressed_pubkey": trace.final_pubkey,
            "hash160": trace.hash160,
            "derived_address": trace.address,
            "target_address": TARGET_ADDRESS,
        },
        sort_keys=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate exactly one passphrase candidate locally.")
    parser.add_argument("candidate", nargs="?", help="one literal BIP39 passphrase candidate")
    parser.add_argument("--mode", choices=[mode.value for mode in NormalizationMode], default="standard")
    parser.add_argument("--debug", action="store_true", help="print only hashed/public intermediate diagnostics")
    parser.add_argument("--selftest", action="store_true", help="run protocol and puzzle reconstruction tests, then stop")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        if args.candidate is not None or args.debug or args.mode != "standard":
            parser.error("--selftest cannot be combined with candidate, --debug, or compatibility mode")
        try:
            checks = run_selftest()
        except OracleError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(checks, sort_keys=True))
        return 0
    if args.candidate is None:
        parser.error("exactly one candidate is required unless --selftest is used")
    try:
        trace = derive_candidate(args.candidate, args.mode)
    except (OracleError, TypeError, ValueError) as exc:
        print("ERROR")
        if args.debug:
            print(json.dumps({"error_type": type(exc).__name__}))
        return 2
    result = OracleResult.MATCH if trace.address == TARGET_ADDRESS else OracleResult.NO_MATCH
    print(result.value)
    if args.debug:
        print(_safe_debug(trace))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
