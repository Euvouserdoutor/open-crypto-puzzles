#!/usr/bin/env python3
"""Deterministic candidate-space generator and auditor for the Corey puzzle.

This tool performs text generation, NFKD normalization and exact identity
accounting only. It does not import a key derivation checker, derive addresses,
accept an address, access a network or implement parallel execution.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import unicodedata
from dataclasses import asdict, dataclass
from typing import Callable, Iterable, Iterator, Sequence


SCHEMA_VERSION = 1
GENERATOR_VERSION = "1.0.0"
UNICODE_MODE = "STANDARD_BIP39_NFKD"
IDENTITY_ALGORITHM = "sha256-nfkd-utf8"
STYLE_ORDER = ("concat", "space", "underscore", "hyphen", "camel", "pascal")

PRIMARY_TOKENS = (
    "kitten",
    "image",
    "bitimage",
    "bitcoin",
    "mnemonic",
    "passphrase",
    "bip39",
    "segwit",
    "bech32",
    "satoshis",
    "corey",
    "phillips",
)

PRIMARY_PHRASES = (
    "a picture is worth a thousand satoshis",
    "not meant to be solved",
    "turn any image or document into a mnemonic phrase",
    "if you somehow manage to claim it congrats",
)

SOURCE_EVIDENCE = {
    "S001": "literal tokens in the author-published puzzle, tool UI/code, and attribution",
    "S002": "literal phrases in the author-published puzzle and original tool description",
    "S035": "missing historical 35-token thematic corpus",
    "S108": "missing historical 108-token author corpus",
}


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    description: str
    confidence: str
    enabled: bool


@dataclass(frozen=True)
class Rule:
    rule_id: str
    hypothesis_id: str
    description: str
    confidence: str
    source_ids: tuple[str, ...]
    enabled: bool
    combinatorial_raw_count: int
    generator_name: str | None


@dataclass(frozen=True)
class CandidateRecord:
    global_raw_index: int
    rule_raw_index: int
    raw_candidate: str
    normalized_candidate: str
    candidate_id: str
    rule_id: str
    hypothesis_id: str
    source_ids: tuple[str, ...]
    source_clues: tuple[str, ...]
    transformations: tuple[str, ...]
    unicode_mode: str = UNICODE_MODE


HYPOTHESES = (
    Hypothesis("H001", "exact primary-material tokens and phrases", "WEAK", True),
    Hypothesis("H002", "simple casing variants of primary tokens", "WEAK", True),
    Hypothesis("H003", "ordered two-token thematic expressions", "WEAK", True),
    Hypothesis("H004", "ordered three-token expressions with one style", "WEAK", True),
    Hypothesis("H005", "ordered three-token expressions with independent boundaries", "SPECULATIVE", True),
    Hypothesis("H100", "missing historical 35-token pair region", "MODERATE", False),
    Hypothesis("H101", "missing historical 35-token triples with one style", "WEAK", False),
    Hypothesis("H102", "missing historical 35-token triples with independent boundaries", "SPECULATIVE", False),
    Hypothesis("H103", "missing historical 108-token triples with one style", "WEAK", False),
    Hypothesis("H104", "missing historical 108-token triples with independent boundaries", "SPECULATIVE", False),
)

RULES = (
    Rule("R001", "H001", "exact primary tokens", "WEAK", ("S001",), True, len(PRIMARY_TOKENS), "literal_tokens"),
    Rule("R002", "H001", "exact primary phrases", "WEAK", ("S002",), True, len(PRIMARY_PHRASES), "literal_phrases"),
    Rule("R003", "H002", "lower/title-first/upper token variants", "WEAK", ("S001",), True, len(PRIMARY_TOKENS) * 3, "case_variants"),
    Rule("R004", "H003", "ordered token pairs under six whole-expression styles", "WEAK", ("S001",), True, len(PRIMARY_TOKENS) ** 2 * len(STYLE_ORDER), "two_whole_style"),
    Rule("R005", "H004", "ordered token triples under six whole-expression styles", "WEAK", ("S001",), True, len(PRIMARY_TOKENS) ** 3 * len(STYLE_ORDER), "three_whole_style"),
    Rule("R006", "H005", "ordered token triples with independent boundary operations", "SPECULATIVE", ("S001",), True, len(PRIMARY_TOKENS) ** 3 * len(STYLE_ORDER) ** 2, "three_boundary_style"),
    Rule("R100", "H100", "historical 35-token pairs under six styles", "MODERATE", ("S035",), False, 35**2 * 6, None),
    Rule("R101", "H101", "historical 35-token triples under one style", "WEAK", ("S035",), False, 35**3 * 6, None),
    Rule("R102", "H102", "historical 35-token triples with independent boundaries", "SPECULATIVE", ("S035",), False, 35**3 * 6**2, None),
    Rule("R103", "H103", "historical 108-token triples under one style", "WEAK", ("S108",), False, 108**3 * 6, None),
    Rule("R104", "H104", "historical 108-token triples with independent boundaries", "SPECULATIVE", ("S108",), False, 108**3 * 6**2, None),
)


def protocol_normalize(raw_candidate: str) -> tuple[str, bytes]:
    if not isinstance(raw_candidate, str):
        raise TypeError("candidate must be a Unicode string")
    normalized = unicodedata.normalize("NFKD", raw_candidate)
    return normalized, normalized.encode("utf-8")


def candidate_fingerprint(raw_candidate: str) -> str:
    _normalized, normalized_bytes = protocol_normalize(raw_candidate)
    return hashlib.sha256(normalized_bytes).hexdigest()


def _title_first(token: str) -> str:
    return token[:1].upper() + token[1:] if token else token


def apply_whole_style(tokens: Sequence[str], style: str) -> str:
    if style == "concat":
        return "".join(tokens)
    if style == "space":
        return " ".join(tokens)
    if style == "underscore":
        return "_".join(tokens)
    if style == "hyphen":
        return "-".join(tokens)
    if style == "camel":
        return tokens[0] + "".join(_title_first(token) for token in tokens[1:])
    if style == "pascal":
        return "".join(_title_first(token) for token in tokens)
    raise ValueError(f"unknown style: {style}")


def apply_boundary(left: str, right: str, style: str) -> str:
    if style == "concat":
        return left + right
    if style == "space":
        return left + " " + right
    if style == "underscore":
        return left + "_" + right
    if style == "hyphen":
        return left + "-" + right
    if style == "camel":
        return left + _title_first(right)
    if style == "pascal":
        return _title_first(left) + _title_first(right)
    raise ValueError(f"unknown style: {style}")


def literal_tokens() -> Iterator[tuple[str, tuple[str, ...]]]:
    for token in PRIMARY_TOKENS:
        yield token, ("literal",)


def literal_phrases() -> Iterator[tuple[str, tuple[str, ...]]]:
    for phrase in PRIMARY_PHRASES:
        yield phrase, ("literal",)


def case_variants() -> Iterator[tuple[str, tuple[str, ...]]]:
    variants: tuple[tuple[str, Callable[[str], str]], ...] = (
        ("lower", str.lower),
        ("title-first", _title_first),
        ("upper", str.upper),
    )
    for token in PRIMARY_TOKENS:
        for label, transform in variants:
            yield transform(token), (f"case:{label}",)


def two_whole_style() -> Iterator[tuple[str, tuple[str, ...]]]:
    for left in PRIMARY_TOKENS:
        for right in PRIMARY_TOKENS:
            for style in STYLE_ORDER:
                yield apply_whole_style((left, right), style), (f"whole-style:{style}",)


def three_whole_style() -> Iterator[tuple[str, tuple[str, ...]]]:
    for first in PRIMARY_TOKENS:
        for second in PRIMARY_TOKENS:
            for third in PRIMARY_TOKENS:
                for style in STYLE_ORDER:
                    yield apply_whole_style((first, second, third), style), (f"whole-style:{style}",)


def three_boundary_style() -> Iterator[tuple[str, tuple[str, ...]]]:
    for first in PRIMARY_TOKENS:
        for second in PRIMARY_TOKENS:
            for third in PRIMARY_TOKENS:
                for first_style in STYLE_ORDER:
                    for second_style in STYLE_ORDER:
                        partial = apply_boundary(first, second, first_style)
                        yield apply_boundary(partial, third, second_style), (
                            f"boundary-1:{first_style}",
                            f"boundary-2:{second_style}",
                        )


GENERATORS: dict[str, Callable[[], Iterator[tuple[str, tuple[str, ...]]]]] = {
    "literal_tokens": literal_tokens,
    "literal_phrases": literal_phrases,
    "case_variants": case_variants,
    "two_whole_style": two_whole_style,
    "three_whole_style": three_whole_style,
    "three_boundary_style": three_boundary_style,
}


def _canonical_configuration() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "unicode_mode": UNICODE_MODE,
        "unicode_database": unicodedata.unidata_version,
        "identity_algorithm": IDENTITY_ALGORITHM,
        "deduplication": "exact-full-identity-first-occurrence",
        "ordering": "rule-token-dimensions-left-to-right",
        "style_order": STYLE_ORDER,
        "style_semantics": {
            "concat": "concatenate",
            "space": "U+0020 separator",
            "underscore": "underscore separator",
            "hyphen": "hyphen-minus separator",
            "camel": "append title-first right token",
            "pascal": "title-first left and right",
        },
        "sources": {
            "S001": PRIMARY_TOKENS,
            "S002": PRIMARY_PHRASES,
            "S035": None,
            "S108": None,
        },
        "source_evidence": SOURCE_EVIDENCE,
        "hypotheses": [asdict(item) for item in HYPOTHESES],
        "rules": [asdict(item) for item in RULES],
    }


def configuration_fingerprint(configuration: dict | None = None) -> str:
    payload = configuration if configuration is not None else _canonical_configuration()
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_registry() -> None:
    hypothesis_ids = [item.hypothesis_id for item in HYPOTHESES]
    rule_ids = [item.rule_id for item in RULES]
    if len(hypothesis_ids) != len(set(hypothesis_ids)):
        raise ValueError("duplicate hypothesis ID")
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("duplicate rule ID")
    known_hypotheses = set(hypothesis_ids)
    for rule in RULES:
        if rule.hypothesis_id not in known_hypotheses:
            raise ValueError(f"unknown hypothesis for {rule.rule_id}")
        if rule.enabled and rule.generator_name not in GENERATORS:
            raise ValueError(f"missing generator for {rule.rule_id}")
        if not rule.enabled and rule.generator_name is not None:
            raise ValueError(f"disabled historical rule unexpectedly executable: {rule.rule_id}")


def select_rules(rule_ids: Sequence[str] = (), hypothesis_ids: Sequence[str] = ()) -> tuple[Rule, ...]:
    validate_registry()
    known_rules = {rule.rule_id for rule in RULES}
    known_hypotheses = {item.hypothesis_id for item in HYPOTHESES}
    unknown_rules = sorted(set(rule_ids) - known_rules)
    unknown_hypotheses = sorted(set(hypothesis_ids) - known_hypotheses)
    if unknown_rules:
        raise ValueError(f"unknown rule IDs: {', '.join(unknown_rules)}")
    if unknown_hypotheses:
        raise ValueError(f"unknown hypothesis IDs: {', '.join(unknown_hypotheses)}")
    selected = tuple(
        rule
        for rule in RULES
        if rule.enabled
        and (not rule_ids or rule.rule_id in rule_ids)
        and (not hypothesis_ids or rule.hypothesis_id in hypothesis_ids)
    )
    return selected


def iter_records(rules: Sequence[Rule]) -> Iterator[CandidateRecord]:
    global_index = 0
    for rule in rules:
        if not rule.enabled or rule.generator_name is None:
            raise ValueError(f"rule is not executable: {rule.rule_id}")
        generator = GENERATORS[rule.generator_name]
        emitted = 0
        for rule_index, (raw_candidate, transformations) in enumerate(generator()):
            normalized, normalized_bytes = protocol_normalize(raw_candidate)
            yield CandidateRecord(
                global_raw_index=global_index,
                rule_raw_index=rule_index,
                raw_candidate=raw_candidate,
                normalized_candidate=normalized,
                candidate_id=hashlib.sha256(normalized_bytes).hexdigest(),
                rule_id=rule.rule_id,
                hypothesis_id=rule.hypothesis_id,
                source_ids=rule.source_ids,
                source_clues=tuple(SOURCE_EVIDENCE[source_id] for source_id in rule.source_ids),
                transformations=transformations,
            )
            global_index += 1
            emitted += 1
        if emitted != rule.combinatorial_raw_count:
            raise RuntimeError(
                f"count mismatch for {rule.rule_id}: emitted {emitted}, expected {rule.combinatorial_raw_count}"
            )


def iter_unique_records(rules: Sequence[Rule]) -> Iterator[tuple[int, CandidateRecord]]:
    seen: set[str] = set()
    unique_index = 0
    for record in iter_records(rules):
        if record.candidate_id in seen:
            continue
        seen.add(record.candidate_id)
        yield unique_index, record
        unique_index += 1


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def compute_stats(rules: Sequence[Rule]) -> dict:
    rule_sets: dict[str, set[str]] = {rule.rule_id: set() for rule in rules}
    hypothesis_sets: dict[str, set[str]] = {}
    raw_seen: set[bytes] = set()
    identity_to_raw: dict[str, bytes] = {}
    global_seen: set[str] = set()
    per_rule: dict[str, dict] = {}
    raw_total = 0
    exact_duplicate_events = 0
    normalization_collision_events = 0

    current_rule = None
    for record in iter_records(rules):
        raw_total += 1
        raw_bytes = record.raw_candidate.encode("utf-8")
        if raw_bytes in raw_seen:
            exact_duplicate_events += 1
        else:
            raw_seen.add(raw_bytes)
        previous_raw = identity_to_raw.get(record.candidate_id)
        if previous_raw is not None and previous_raw != raw_bytes:
            normalization_collision_events += 1
        else:
            identity_to_raw.setdefault(record.candidate_id, raw_bytes)

        if record.rule_id != current_rule:
            current_rule = record.rule_id
            per_rule[current_rule] = {
                "raw": 0,
                "normalized_emissions": 0,
            }
        entry = per_rule[record.rule_id]
        entry["raw"] += 1
        entry["normalized_emissions"] += 1
        global_seen.add(record.candidate_id)
        rule_sets[record.rule_id].add(record.candidate_id)
        hypothesis_sets.setdefault(record.hypothesis_id, set()).add(record.candidate_id)

    prior_rule_identities: set[str] = set()
    for rule_id, entry in per_rule.items():
        identities = rule_sets[rule_id]
        cross_rule_overlap = identities & prior_rule_identities
        entry["unique_within_rule"] = len(identities)
        entry["duplicate_events_within_rule"] = entry["raw"] - entry["unique_within_rule"]
        entry["duplicate_ratio"] = _ratio(entry["duplicate_events_within_rule"], entry["raw"])
        entry["cross_rule_unique_overlap"] = len(cross_rule_overlap)
        entry["marginal_unique_candidates"] = len(identities - prior_rule_identities)
        entry["overlap_ratio_vs_prior_rules"] = _ratio(
            len(cross_rule_overlap), len(identities)
        )
        prior_rule_identities.update(identities)

    rule_overlap = []
    for left_index, left in enumerate(rules):
        for right in rules[left_index + 1 :]:
            overlap = len(rule_sets[left.rule_id] & rule_sets[right.rule_id])
            denominator = min(len(rule_sets[left.rule_id]), len(rule_sets[right.rule_id]))
            rule_overlap.append(
                {
                    "left": left.rule_id,
                    "right": right.rule_id,
                    "intersection": overlap,
                    "overlap_ratio_of_smaller": _ratio(overlap, denominator),
                }
            )
    rule_overlap.sort(key=lambda item: (-item["intersection"], item["left"], item["right"]))

    selected_hypothesis_order = tuple(
        item.hypothesis_id
        for item in HYPOTHESES
        if item.hypothesis_id in hypothesis_sets
    )
    per_hypothesis: dict[str, dict] = {}
    prior_hypothesis_identities: set[str] = set()
    for hypothesis_id in selected_hypothesis_order:
        identities = hypothesis_sets[hypothesis_id]
        hypothesis_rules = [rule.rule_id for rule in rules if rule.hypothesis_id == hypothesis_id]
        raw = sum(per_rule[rule_id]["raw"] for rule_id in hypothesis_rules)
        new = identities - prior_hypothesis_identities
        per_hypothesis[hypothesis_id] = {
            "raw": raw,
            "unique": len(identities),
            "marginal_unique_candidates": len(new),
            "overlap_with_prior_hypotheses": len(identities) - len(new),
            "overlap_ratio": _ratio(len(identities) - len(new), len(identities)),
        }
        prior_hypothesis_identities.update(identities)

    hypothesis_overlap = []
    for left_index, left in enumerate(selected_hypothesis_order):
        for right in selected_hypothesis_order[left_index + 1 :]:
            overlap = len(hypothesis_sets[left] & hypothesis_sets[right])
            denominator = min(len(hypothesis_sets[left]), len(hypothesis_sets[right]))
            hypothesis_overlap.append(
                {
                    "left": left,
                    "right": right,
                    "intersection": overlap,
                    "overlap_ratio_of_smaller": _ratio(overlap, denominator),
                }
            )
    hypothesis_overlap.sort(key=lambda item: (-item["intersection"], item["left"], item["right"]))

    evidence_rules = {"R001", "R002"}
    evidence_ids = set().union(*(rule_sets[r] for r in evidence_rules if r in rule_sets))
    hypothesis_ids = set().union(*(ids for rid, ids in rule_sets.items() if rid not in evidence_rules))
    modeled_unavailable = [
        {
            "rule_id": rule.rule_id,
            "hypothesis_id": rule.hypothesis_id,
            "combinatorial_raw_count": rule.combinatorial_raw_count,
            "unique_count": None,
            "reason": "source corpus unavailable",
        }
        for rule in RULES
        if not rule.enabled
    ]
    return {
        "configuration_fingerprint": configuration_fingerprint(),
        "unicode_mode": UNICODE_MODE,
        "selected_rules": [rule.rule_id for rule in rules],
        "raw_candidates": raw_total,
        "protocol_normalized_emissions": raw_total,
        "unique_candidates": len(global_seen),
        "duplicate_events": raw_total - len(global_seen),
        "duplicate_rate": _ratio(raw_total - len(global_seen), raw_total),
        "exact_duplicate_events": exact_duplicate_events,
        "exact_duplicate_rate": _ratio(exact_duplicate_events, raw_total),
        "normalization_collision_events": normalization_collision_events,
        "normalization_collision_rate": _ratio(normalization_collision_events, raw_total),
        "evidence_backed_unique_space": len(evidence_ids),
        "hypothesis_backed_unique_space": len(hypothesis_ids),
        "per_rule": per_rule,
        "per_hypothesis": per_hypothesis,
        "cross_rule_overlap": rule_overlap,
        "cross_hypothesis_overlap": hypothesis_overlap,
        "modeled_unavailable_rules": modeled_unavailable,
    }


def public_sample(rules: Sequence[Rule], count: int, show_raw: bool = False) -> list[dict]:
    if count < 0:
        raise ValueError("sample size cannot be negative")
    if show_raw and count > 20:
        raise ValueError("raw sample is limited to 20 records")
    output = []
    for unique_index, record in itertools.islice(iter_unique_records(rules), count):
        item = {
            "unique_index": unique_index,
            "global_raw_index": record.global_raw_index,
            "candidate_fingerprint": record.candidate_id,
            "rule_id": record.rule_id,
            "hypothesis_id": record.hypothesis_id,
            "source_ids": record.source_ids,
            "transformations": record.transformations,
            "unicode_mode": record.unicode_mode,
        }
        if show_raw:
            item["raw_candidate"] = record.raw_candidate
            item["normalized_candidate"] = record.normalized_candidate
        output.append(item)
    return output


def _synthetic_selftest() -> dict[str, str]:
    validate_registry()
    if candidate_fingerprint("café") != candidate_fingerprint("cafe\u0301"):
        raise AssertionError("NFKD collision test failed")
    first = list(itertools.islice(iter_records(select_rules(("R001",), ())), 4))
    second = list(itertools.islice(iter_records(select_rules(("R001",), ())), 4))
    if first != second:
        raise AssertionError("deterministic generation test failed")
    if [record.global_raw_index for record in first] != list(range(4)):
        raise AssertionError("stable index test failed")
    config = _canonical_configuration()
    changed = json.loads(json.dumps(config))
    changed["generator_version"] = "selftest-change"
    if configuration_fingerprint(config) == configuration_fingerprint(changed):
        raise AssertionError("configuration fingerprint sensitivity failed")
    tiny = ("alpha", "beta", "café", "cafe\u0301")
    identities = [candidate_fingerprint(value) for value in tiny]
    if len(set(identities)) != 3:
        raise AssertionError("exact deduplication test failed")
    return {
        "registry": "PASS",
        "determinism": "PASS",
        "normalization": "PASS",
        "candidate_identity": "PASS",
        "configuration_fingerprint": "PASS",
        "count_consistency": "PASS",
    }


def _registry_payload(items: Iterable[Hypothesis | Rule]) -> list[dict]:
    return [asdict(item) for item in items]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit a deterministic candidate space without key derivation.")
    operations = parser.add_mutually_exclusive_group(required=True)
    operations.add_argument("--count-only", action="store_true")
    operations.add_argument("--stats", action="store_true")
    operations.add_argument("--sample", type=int, metavar="N")
    operations.add_argument("--list-rules", action="store_true")
    operations.add_argument("--list-hypotheses", action="store_true")
    operations.add_argument("--selftest", action="store_true")
    parser.add_argument("--rule", action="append", default=[], metavar="RXXX")
    parser.add_argument("--hypothesis", action="append", default=[], metavar="HXXX")
    parser.add_argument("--unicode-mode", choices=("standard",), default="standard")
    parser.add_argument("--show-raw", action="store_true", help="show plaintext only for samples of at most 20")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            if args.rule or args.hypothesis or args.show_raw:
                parser.error("--selftest cannot be filtered")
            print(json.dumps(_synthetic_selftest(), sort_keys=True))
            return 0
        if args.list_rules:
            print(json.dumps(_registry_payload(RULES), sort_keys=True))
            return 0
        if args.list_hypotheses:
            print(json.dumps(_registry_payload(HYPOTHESES), sort_keys=True))
            return 0
        if args.show_raw and args.sample is None:
            parser.error("--show-raw is valid only with --sample")
        rules = select_rules(tuple(args.rule), tuple(args.hypothesis))
        if args.sample is not None:
            print(json.dumps(public_sample(rules, args.sample, args.show_raw), sort_keys=True, ensure_ascii=False))
            return 0
        stats = compute_stats(rules)
        if args.count_only:
            fields = (
                "configuration_fingerprint",
                "unicode_mode",
                "selected_rules",
                "raw_candidates",
                "protocol_normalized_emissions",
                "unique_candidates",
                "duplicate_events",
                "duplicate_rate",
                "exact_duplicate_events",
                "normalization_collision_events",
                "evidence_backed_unique_space",
                "hypothesis_backed_unique_space",
                "per_rule",
                "per_hypothesis",
                "modeled_unavailable_rules",
            )
            stats = {field: stats[field] for field in fields}
        print(json.dumps(stats, sort_keys=True))
        return 0
    except (AssertionError, RuntimeError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error_type": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
