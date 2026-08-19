"""Synthetic, structural, and CLI safety tests for the Phase 9 solver."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import corey_solver as solver  # noqa: E402


class TestSyntheticEngine(unittest.TestCase):
    def test_selftest_uses_independent_synthetic_values(self):
        self.assertEqual(set(solver.run_selftest().values()), {"PASS"})

    def test_disjoint_first_occurrence_assignment(self):
        alpha = solver._synthetic_record("alpha", "R901", "H901")
        beta = solver._synthetic_record("beta", "R902", "H902")
        rows = list(solver._iter_disjoint_rows(((1, (alpha,)), (2, (alpha, beta)))))
        self.assertEqual([(row.tier, row.raw_candidate) for row in rows], [(1, "alpha"), (2, "beta")])

    def test_nfkd_is_part_of_identity(self):
        left = solver._synthetic_record("café", "R901", "H901")
        right = solver._synthetic_record("cafe\u0301", "R902", "H902")
        self.assertEqual(left.candidate_id, right.candidate_id)

    def test_checkpoint_rejects_fingerprint_change(self):
        payload = solver._checkpoint_payload(solver.new_checkpoint(1))
        payload["candidate_config_fingerprint"] = "f" * 64
        with self.assertRaises(solver.SolverError):
            solver._parse_checkpoint(payload)


class TestCurrentTierContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = solver.validate_current_partition()

    def test_exact_counts_and_union(self):
        self.assertEqual(
            self.report["tier_counts"],
            {"1": 16, "2": 24, "3": 864, "4": 10_368, "5": 48_384},
        )
        self.assertEqual(self.report["total_unique"], 59_656)
        self.assertEqual(self.report["pairwise_overlap"], 0)

    def test_no_oracle_was_called(self):
        self.assertEqual(self.report["real_oracle_calls"], 0)


class TestCheckpointAndCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "corey_solver.py"), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_selftest(self):
        completed = self.run_cli("--selftest")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(set(json.loads(completed.stdout).values()), {"PASS"})

    def test_dry_run_checkpoint_and_resume_without_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            first = self.run_cli(
                "--dry-run", "--tier", "2", "--max-candidates", "2", "--checkpoint", str(path)
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(json.loads(first.stdout)["evaluated_candidate_count"], 0)
            second = self.run_cli(
                "--dry-run", "--tier", "2", "--max-candidates", "3", "--resume", str(path)
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["next_ordinal"], 5)
            self.assertEqual(payload["evaluated_candidate_count"], 0)
            serialized = path.read_text(encoding="utf-8")
            self.assertNotIn("raw_candidate", serialized)
            self.assertNotIn("normalized_candidate", serialized)

    def test_dry_run_requires_explicit_limit_and_checkpoint(self):
        completed = self.run_cli("--dry-run", "--tier", "1")
        self.assertNotEqual(completed.returncode, 0)

    def test_real_search_interfaces_do_not_exist(self):
        help_text = self.run_cli("--help").stdout
        for forbidden in (
            "--search", "--target", "--oracle", "--candidate", "--workers",
            "--threads", "--gpu", "--address", "--broadcast",
        ):
            self.assertNotIn(forbidden, help_text)


if __name__ == "__main__":
    unittest.main()
