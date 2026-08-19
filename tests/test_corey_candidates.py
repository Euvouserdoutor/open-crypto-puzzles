"""Synthetic and structural tests for the Corey candidate-space generator."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))
import corey_candidates as candidates  # noqa: E402


def synthetic_rule(testcase, rule_id, hypothesis_id, values):
    generator_name = f"synthetic_{rule_id.lower()}"

    def generate():
        for value in values:
            yield value, ("synthetic",)

    candidates.GENERATORS[generator_name] = generate
    testcase.addCleanup(candidates.GENERATORS.pop, generator_name, None)
    return candidates.Rule(
        rule_id,
        hypothesis_id,
        "synthetic test rule",
        "WEAK",
        (),
        True,
        len(values),
        generator_name,
    )


class TestNormalizationAndIdentity(unittest.TestCase):
    def test_nfkd_collision(self):
        self.assertEqual(candidates.candidate_fingerprint("café"), candidates.candidate_fingerprint("cafe\u0301"))

    def test_case_and_whitespace_are_significant(self):
        self.assertNotEqual(candidates.candidate_fingerprint("Kitten"), candidates.candidate_fingerprint("kitten"))
        self.assertNotEqual(candidates.candidate_fingerprint("kitten"), candidates.candidate_fingerprint("kitten "))

    def test_fingerprint_is_full_sha256_hex(self):
        value = candidates.candidate_fingerprint("synthetic")
        self.assertEqual(len(value), 64)
        int(value, 16)


class TestRuleDeterminismAndOrdering(unittest.TestCase):
    def test_rule_determinism_and_stable_indices(self):
        rules = (synthetic_rule(self, "R901", "H001", ("alpha", "beta", "gamma")),)
        first = list(candidates.iter_records(rules))
        second = list(candidates.iter_records(rules))
        self.assertEqual(first, second)
        self.assertEqual([record.global_raw_index for record in first], list(range(len(first))))
        self.assertEqual([record.rule_raw_index for record in first], list(range(len(first))))

    def test_known_order_prefix(self):
        values = ("alpha", "alpha beta", "alpha_beta", "alpha-beta")
        rule = synthetic_rule(self, "R902", "H001", values)
        records = list(candidates.iter_records((rule,)))
        self.assertEqual([record.raw_candidate for record in records], list(values))

    def test_rule_counts_match_combinatorial_contract(self):
        rule = synthetic_rule(self, "R903", "H001", ("alpha", "beta", "gamma"))
        self.assertEqual(sum(1 for _ in candidates.iter_records((rule,))), 3)

    def test_empty_rule_selection(self):
        self.assertEqual(candidates.select_rules((), ("H100",)), ())
        stats = candidates.compute_stats(())
        self.assertEqual(stats["raw_candidates"], 0)
        self.assertEqual(stats["unique_candidates"], 0)


class TestProvenanceFilteringAndDedup(unittest.TestCase):
    def test_provenance_is_preserved(self):
        rule = synthetic_rule(self, "R904", "H001", ("alpha",))
        record = next(candidates.iter_records((rule,)))
        self.assertEqual(record.rule_id, "R904")
        self.assertEqual(record.hypothesis_id, "H001")
        self.assertEqual(record.source_ids, ())
        self.assertEqual(record.source_clues, ())
        self.assertEqual(record.transformations, ("synthetic",))

    def test_hypothesis_filter_excludes_other_rules(self):
        records = list(candidates.iter_records(candidates.select_rules((), ("H001",))))
        self.assertEqual({record.hypothesis_id for record in records}, {"H001"})
        self.assertEqual({record.rule_id for record in records}, {"R001", "R002"})

    def test_cross_rule_duplicates_are_detected(self):
        left = synthetic_rule(self, "R905", "H001", ("alpha", "beta", "café"))
        right = synthetic_rule(self, "R906", "H002", ("beta", "gamma", "cafe\u0301"))
        stats = candidates.compute_stats((left, right))
        self.assertEqual(stats["raw_candidates"], 6)
        self.assertEqual(stats["unique_candidates"], 4)
        self.assertEqual(stats["per_rule"]["R906"]["cross_rule_unique_overlap"], 2)

    def test_internal_duplicates_are_not_cross_rule_overlap(self):
        rule = synthetic_rule(self, "R907", "H001", ("alpha", "alpha", "beta"))
        stats = candidates.compute_stats((rule,))
        self.assertEqual(stats["per_rule"]["R907"]["duplicate_events_within_rule"], 1)
        self.assertEqual(stats["per_rule"]["R907"]["cross_rule_unique_overlap"], 0)

    def test_unique_indices_follow_first_occurrence(self):
        left = synthetic_rule(self, "R908", "H001", ("alpha", "beta"))
        right = synthetic_rule(self, "R909", "H002", ("beta", "gamma"))
        records = list(candidates.iter_unique_records((left, right)))
        self.assertEqual([index for index, _record in records], list(range(len(records))))
        self.assertEqual(records[0][1].rule_id, "R908")


class TestConfigurationFingerprint(unittest.TestCase):
    def test_stable_across_calls(self):
        self.assertEqual(candidates.configuration_fingerprint(), candidates.configuration_fingerprint())

    def test_changes_with_semantics(self):
        config = candidates._canonical_configuration()
        changed = dict(config)
        changed["ordering"] = "synthetic-different-order"
        self.assertNotEqual(candidates.configuration_fingerprint(config), candidates.configuration_fingerprint(changed))

    def test_registry_rejects_enabled_rule_without_generator(self):
        original = candidates.RULES
        try:
            candidates.RULES = original + (
                replace(original[0], rule_id="R999", generator_name="missing"),
            )
            with self.assertRaises(ValueError):
                candidates.validate_registry()
        finally:
            candidates.RULES = original


class TestCliSafetyAndSelftest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "corey_candidates.py"), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_selftest(self):
        completed = self.run_cli("--selftest")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(set(json.loads(completed.stdout).values()), {"PASS"})

    def test_count_only_includes_rule_and_hypothesis_breakdown(self):
        completed = self.run_cli("--count-only", "--rule", "R001")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(set(payload["per_rule"]), {"R001"})
        self.assertEqual(set(payload["per_hypothesis"]), {"H001"})

    def test_sample_redacts_plaintext_by_default(self):
        completed = self.run_cli("--sample", "2")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("raw_candidate", completed.stdout)
        self.assertNotIn(candidates.PRIMARY_TOKENS[0], completed.stdout)

    def test_show_raw_is_bounded(self):
        completed = self.run_cli("--sample", "21", "--show-raw")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(json.loads(completed.stderr)["status"], "ERROR")

    def test_no_unsafe_cli_flags_exist(self):
        help_text = self.run_cli("--help").stdout
        for forbidden in ("--search", "--target", "--oracle", "--bruteforce", "--workers", "--gpu", "--threads", "--scan"):
            self.assertNotIn(forbidden, help_text)


if __name__ == "__main__":
    unittest.main()
