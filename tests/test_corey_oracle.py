"""Tests for the single-candidate Corey Phillips puzzle oracle."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import corey_oracle as oracle  # noqa: E402


class TestBIP39AndUnicode(unittest.TestCase):
    def test_official_bip39_vector(self):
        phrase = "abandon " * 11 + "about"
        expected = (
            "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e5349553"
            "1f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"
        )
        self.assertEqual(oracle.bip39_seed(phrase, "TREZOR").hex(), expected)

    def test_nfkd_equivalence_and_raw_isolation(self):
        phrase = "abandon " * 11 + "about"
        self.assertEqual(oracle.bip39_seed(phrase, "é"), oracle.bip39_seed(phrase, "e\u0301"))
        self.assertNotEqual(
            oracle.bip39_seed(phrase, "é", "raw-compat"),
            oracle.bip39_seed(phrase, "e\u0301", "raw-compat"),
        )

    def test_nfkd_does_not_strip_space_or_change_case(self):
        self.assertNotEqual(oracle.bip39_seed("Abandon", "x"), oracle.bip39_seed("abandon", "x"))
        self.assertNotEqual(oracle.bip39_seed("abandon", "x"), oracle.bip39_seed("abandon", " x"))


class TestProtocolLayers(unittest.TestCase):
    def test_bip32_master_and_hardened_child_vector(self):
        master, chain = oracle.master_from_seed(bytes.fromhex("000102030405060708090a0b0c0d0e0f"))
        self.assertEqual(f"{master:064x}", "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35")
        self.assertEqual(chain.hex(), "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508")
        child, child_chain = oracle.ckd_private(master, chain, 0x80000000)
        self.assertEqual(f"{child:064x}", "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea")
        self.assertEqual(child_chain.hex(), "47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141")

    def test_secp256k1_generator_vector(self):
        self.assertEqual(
            oracle.compressed_public_key(1).hex(),
            "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
        )

    def test_bip173_round_trip_vector(self):
        program = bytes.fromhex("751e76e8199196d454941c45d1b3a323f1433bd6")
        address = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
        self.assertEqual(oracle.encode_segwit_v0(program), address)
        self.assertEqual(oracle.decode_segwit_address(address), ("bc", 0, program))


class TestPuzzleReconstruction(unittest.TestCase):
    def test_image_to_mnemonic_is_reconstructed(self):
        image = REPO_ROOT / oracle.PUZZLE_RELATIVE_IMAGE
        raw_digest, mnemonic, entropy = oracle.reconstruct_puzzle_mnemonic(image)
        self.assertEqual(raw_digest, oracle.EXPECTED_IMAGE_SHA256)
        self.assertEqual(entropy.hex(), oracle.EXPECTED_ENTROPY_HEX)
        self.assertEqual(mnemonic, " ".join(oracle.EXPECTED_WORDS))
        self.assertEqual(oracle.entropy_to_indices(entropy), oracle.EXPECTED_WORD_INDICES)

    def test_empty_passphrase_reaches_sister_address(self):
        trace = oracle.derive_candidate("")
        self.assertEqual(trace.seed_sha256, oracle.EXPECTED_EMPTY_SEED_SHA256)
        self.assertEqual(trace.master_fingerprint, oracle.EXPECTED_EMPTY_MASTER_FINGERPRINT)
        self.assertEqual(trace.final_pubkey, oracle.EXPECTED_EMPTY_FINAL_PUBKEY)
        self.assertEqual(trace.hash160, oracle.EXPECTED_EMPTY_HASH160)
        self.assertEqual(trace.address, oracle.EXPECTED_EMPTY_ADDRESS)
        self.assertEqual(oracle.verify_candidate(""), oracle.OracleResult.NO_MATCH)

    def test_target_address_structure(self):
        self.assertEqual(
            oracle.decode_segwit_address(oracle.TARGET_ADDRESS),
            ("bc", 0, bytes.fromhex(oracle.TARGET_PROGRAM_HEX)),
        )


class TestDeterminismErrorsAndCli(unittest.TestCase):
    def test_one_synthetic_candidate_is_deterministic(self):
        first = oracle.derive_candidate("synthetic-self-test-only")
        second = oracle.derive_candidate("synthetic-self-test-only")
        self.assertEqual(first, second)
        self.assertEqual(oracle.verify_candidate("synthetic-self-test-only"), oracle.OracleResult.NO_MATCH)

    def test_errors_are_not_no_match(self):
        self.assertEqual(oracle.verify_candidate(None), oracle.OracleResult.ERROR)
        self.assertEqual(oracle.verify_candidate("x", "unknown"), oracle.OracleResult.ERROR)
        with self.assertRaises(oracle.OracleError):
            oracle.decode_segwit_address(oracle.TARGET_ADDRESS[:-1] + "x")

    def test_selftest_groups(self):
        checks = oracle.run_selftest()
        self.assertEqual(set(checks.values()), {"PASS"})
        self.assertEqual(
            set(checks),
            {"bip39_nfkd", "bip32", "secp256k1", "bech32_p2wpkh", "puzzle_reconstruction", "target_structure"},
        )

    def test_cli_is_single_candidate_only_and_debug_redacts_plaintext(self):
        script = REPO_ROOT / "tools" / "corey_oracle.py"
        missing = subprocess.run([sys.executable, str(script)], text=True, capture_output=True, check=False)
        self.assertEqual(missing.returncode, 2)
        secret_marker = "do-not-print-this"
        run = subprocess.run(
            [sys.executable, str(script), "--debug", secret_marker],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(run.returncode, 1)
        self.assertTrue(run.stdout.startswith("NO_MATCH\n"))
        self.assertNotIn(secret_marker, run.stdout + run.stderr)
        self.assertNotIn("private", run.stdout.lower())


if __name__ == "__main__":
    unittest.main()
