"""Differential validation of independent Corey oracle implementations A and B."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import corey_oracle as implementation_a  # noqa: E402


IMPLEMENTATION_B = REPO_ROOT / "tools" / "corey_oracle_b.js"
SYNTHETIC_CORPUS = (
    "",
    "kitten",
    "hello world",
    "123456",
    "café",
    "cafe\u0301",
    "①",
    "ﬁ",
    "e\u0301\u0323",
    "猫",
    " Ω ",
    " leading",
    "trailing ",
    "two  spaces",
    "no\u00a0break",
)


def trace_a(candidate: str, mode: str = "standard", path: str = implementation_a.DERIVATION_PATH):
    candidate_bytes = implementation_a._encode_bip39_text(candidate, mode)
    mnemonic = " ".join(implementation_a.EXPECTED_WORDS)
    mnemonic_bytes = implementation_a._encode_bip39_text(mnemonic, mode)
    seed = implementation_a.bip39_seed(mnemonic, candidate, mode)
    child, _chain, master = implementation_a.derive_private_path(seed, path)
    public = implementation_a.compressed_public_key(child)
    program = implementation_a.hash160(public)
    return {
        "mode": mode,
        "path": path,
        "normalized_mnemonic_sha256": hashlib.sha256(mnemonic_bytes).hexdigest(),
        "normalized_passphrase_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
        "seed_sha256": hashlib.sha256(seed).hexdigest(),
        "master_fingerprint": implementation_a.hash160(implementation_a.compressed_public_key(master))[:4].hex(),
        "child_private_sha256": hashlib.sha256(child.to_bytes(32, "big")).hexdigest(),
        "public_key": public.hex(),
        "hash160": program.hex(),
        "address": implementation_a.encode_segwit_v0(program),
    }


def trace_b(candidate: str, mode: str = "standard", path: str = implementation_a.DERIVATION_PATH):
    completed = subprocess.run(
        ["node", str(IMPLEMENTATION_B), "--mode", mode, "--path", path, "--inspect", candidate],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"Implementation B failed: {completed.stderr}")
    result = json.loads(completed.stdout)
    result.pop("verdict")
    return result


class TestIndependentProtocolVectors(unittest.TestCase):
    def test_implementation_b_selftest(self):
        completed = subprocess.run(
            ["node", str(IMPLEMENTATION_B), "--selftest"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(set(json.loads(completed.stdout).values()), {"PASS"})

    def test_target_decode_agrees(self):
        completed = subprocess.run(
            ["node", str(IMPLEMENTATION_B), "--target-json"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        decoded_b = json.loads(completed.stdout)
        hrp, version, program = implementation_a.decode_segwit_address(implementation_a.TARGET_ADDRESS)
        self.assertEqual(decoded_b, {"hrp": hrp, "version": version, "program": program.hex(), "checksum": "valid"})


class TestDifferentialPipeline(unittest.TestCase):
    def test_fixed_synthetic_unicode_corpus(self):
        for candidate in SYNTHETIC_CORPUS:
            with self.subTest(codepoints=[f"U+{ord(c):04X}" for c in candidate]):
                self.assertEqual(trace_a(candidate), trace_b(candidate))

    def test_raw_compat_is_separate_but_agrees(self):
        candidate = "café"
        standard = trace_a(candidate, "standard")
        raw_a = trace_a(candidate, "raw-compat")
        raw_b = trace_b(candidate, "raw-compat")
        self.assertEqual(raw_a, raw_b)
        self.assertNotEqual(standard["seed_sha256"], raw_a["seed_sha256"])

    def test_path_mutations_propagate_in_both_implementations(self):
        candidate = "controlled-path-vector"
        paths = ("m/84'/0'/0'/0/0", "m/84'/0'/0'/0/1", "m/84'/0'/0'/0'/0")
        results = []
        for path in paths:
            left = trace_a(candidate, path=path)
            right = trace_b(candidate, path=path)
            self.assertEqual(left, right)
            results.append(left["address"])
        self.assertEqual(len(set(results)), len(paths))

    def test_neighboring_controlled_passphrases_change_output(self):
        variants = ("Controlled", "controlled", "controlled ", "controllee")
        traces = [trace_a(value) for value in variants]
        for value, left in zip(variants, traces):
            self.assertEqual(left, trace_b(value))
        self.assertEqual(len({trace["address"] for trace in traces}), len(variants))

    def test_controlled_match_no_match_error_contract(self):
        correct = "synthetic-contract-value"
        synthetic_target = trace_a(correct)["address"]

        def compare(candidate):
            if not isinstance(candidate, str):
                return implementation_a.OracleResult.ERROR
            return (
                implementation_a.OracleResult.MATCH
                if trace_a(candidate)["address"] == synthetic_target
                else implementation_a.OracleResult.NO_MATCH
            )

        self.assertEqual(compare(correct), implementation_a.OracleResult.MATCH)
        self.assertEqual(compare(correct + "x"), implementation_a.OracleResult.NO_MATCH)
        self.assertEqual(compare(None), implementation_a.OracleResult.ERROR)

    def test_implementation_b_fails_closed(self):
        completed = subprocess.run(
            ["node", str(IMPLEMENTATION_B), "--path", "not/a/path", "--inspect", "synthetic"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(json.loads(completed.stderr)["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
