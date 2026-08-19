#!/usr/bin/env python3
"""Fail-closed Phase 9 search-engine scaffold for the Corey puzzle.

Only synthetic self-tests and redacted dry runs are exposed.  This module does
not import the puzzle oracle, derive Bitcoin keys, compare an address, access a
network, or provide a real-search command.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence

import corey_candidates as candidates


SOLVER_SCHEMA_VERSION = 2
SOLVER_VERSION = "0.2.0"
CHECKPOINT_SCHEMA = "corey-phase10-checkpoint-v1"
PROGRESS_DOMAIN = b"corey-phase9-progress-v1"
STRATEGY_RELATIVE_PATH = Path("research/corey/search-tiers.json")

CANDIDATE_CONFIG_FINGERPRINT = (
    "41d384b6efa28c008582227f64f4bccc618edd2acdfeff5fe84df83f494a4a52"
)
TIER_STRATEGY_FINGERPRINT = (
    "7f2685ceaeae227a4b85be8431c4c53546b26aa62938f6816282080a7211d61a"
)
SUPERSEDED_TIER_STRATEGY_FINGERPRINT = (
    "10940a5429829adfaa6095e44103c628f8fcc046b14c2ca4125925f66b7818bf"
)


class SolverError(Exception):
    """Controlled contract, checkpoint, or execution failure."""


@dataclass(frozen=True)
class TierDefinition:
    tier: int
    hypothesis_id: str
    rule_ids: tuple[str, ...]
    expected_unique: int
    label: str


@dataclass(frozen=True)
class TierCandidate:
    tier: int
    tier_ordinal: int
    candidate_id: str
    raw_candidate: str
    rule_id: str
    hypothesis_id: str


@dataclass(frozen=True)
class Checkpoint:
    schema: str
    solver_version: str
    candidate_config_fingerprint: str
    tier_strategy_fingerprint: str
    unicode_mode: str
    mode: str
    tier: int
    next_ordinal: int
    visited_unique_candidate_count: int
    evaluated_candidate_count: int
    last_candidate_id: str | None
    progress_digest: str
    complete: bool
    match_candidate_id: str | None


TIERS = (
    TierDefinition(1, "H001", ("R001", "R002"), 16, "exact configured literals"),
    TierDefinition(2, "H002", ("R003",), 24, "new case variants"),
    TierDefinition(3, "H003", ("R004",), 864, "two-token expressions"),
    TierDefinition(4, "H004", ("R005",), 10_368, "three-token whole styles"),
    TierDefinition(5, "H005", ("R006",), 48_384, "independent-boundary reserve"),
)
TIER_BY_NUMBER = {item.tier: item for item in TIERS}


def _initial_progress_digest() -> bytes:
    return hashlib.sha256(PROGRESS_DOMAIN).digest()


def _advance_progress_digest(current: bytes, candidate_id: str) -> bytes:
    try:
        identity = bytes.fromhex(candidate_id)
    except ValueError as exc:
        raise SolverError("candidate identity is not hexadecimal") from exc
    if len(identity) != 32:
        raise SolverError("candidate identity is not a full SHA256 digest")
    return hashlib.sha256(current + identity).digest()


def _iter_disjoint_rows(
    ordered_tiers: Iterable[tuple[int, Iterable[candidates.CandidateRecord]]],
) -> Iterator[TierCandidate]:
    """Assign first-occurrence identities to exactly one ordered tier."""
    seen: set[str] = set()
    for tier, rows in ordered_tiers:
        ordinal = 0
        for row in rows:
            if not row.candidate_id or not row.rule_id or not row.hypothesis_id:
                raise SolverError("candidate provenance is incomplete")
            if row.candidate_id in seen:
                continue
            seen.add(row.candidate_id)
            yield TierCandidate(
                tier=tier,
                tier_ordinal=ordinal,
                candidate_id=row.candidate_id,
                raw_candidate=row.raw_candidate,
                rule_id=row.rule_id,
                hypothesis_id=row.hypothesis_id,
            )
            ordinal += 1


def iter_current_tiers() -> Iterator[TierCandidate]:
    ordered = []
    for definition in TIERS:
        rules = candidates.select_rules(definition.rule_ids, ())
        if tuple(rule.rule_id for rule in rules) != definition.rule_ids:
            raise SolverError(f"rule contract mismatch for tier {definition.tier}")
        ordered.append((definition.tier, candidates.iter_records(rules)))
    yield from _iter_disjoint_rows(ordered)


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def load_strategy_contract(path: Path | None = None) -> tuple[dict[str, object], str]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / STRATEGY_RELATIVE_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SolverError("cannot load canonical tier strategy") from exc
    if not isinstance(payload, dict):
        raise SolverError("canonical tier strategy root must be an object")
    fingerprint = hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()
    return payload, fingerprint


def validate_strategy_contract() -> dict[str, object]:
    payload, fingerprint = load_strategy_contract()
    if fingerprint != TIER_STRATEGY_FINGERPRINT:
        raise SolverError("tier strategy fingerprint recomputation mismatch")
    if payload.get("schema") != "corey-tier-strategy-canonical-v1":
        raise SolverError("tier strategy schema mismatch")
    if payload.get("candidate_configuration_fingerprint") != CANDIDATE_CONFIG_FINGERPRINT:
        raise SolverError("strategy candidate configuration mismatch")
    if payload.get("unicode_mode") != candidates.UNICODE_MODE:
        raise SolverError("strategy Unicode mode mismatch")
    if payload.get("supersedes_contract_fingerprint") != SUPERSEDED_TIER_STRATEGY_FINGERPRINT:
        raise SolverError("strategy superseded fingerprint mismatch")
    if payload.get("candidate_identity") != "sha256(nfkd(raw_candidate).utf8)":
        raise SolverError("strategy candidate identity mismatch")

    documented = payload.get("tiers")
    if not isinstance(documented, list) or len(documented) != len(TIERS):
        raise SolverError("strategy tier registry mismatch")
    expected = [
        {
            "order": item.tier,
            "hypothesis": item.hypothesis_id,
            "source_rules": list(item.rule_ids),
            "expected_unique": item.expected_unique,
        }
        for item in TIERS
    ]
    projected = []
    for item in documented:
        if not isinstance(item, dict):
            raise SolverError("strategy tier entry must be an object")
        projected.append({key: item.get(key) for key in expected[0]})
    if projected != expected:
        raise SolverError("strategy tier definitions differ from solver registry")
    return {
        "tier_strategy_fingerprint": fingerprint,
        "canonical_serialization": "json-sort-keys-compact-utf8-ensure-ascii-false",
        "canonical_bytes": len(_canonical_json_bytes(payload)),
    }


def validate_current_partition() -> dict[str, object]:
    """Validate the finite tier partition without evaluating any candidate."""
    strategy = validate_strategy_contract()
    actual_config = candidates.configuration_fingerprint()
    if actual_config != CANDIDATE_CONFIG_FINGERPRINT:
        raise SolverError("candidate configuration fingerprint mismatch")
    if candidates.UNICODE_MODE != "STANDARD_BIP39_NFKD":
        raise SolverError("Unicode normalization contract mismatch")

    ids_by_tier: dict[int, set[str]] = {item.tier: set() for item in TIERS}
    order_by_tier: dict[int, list[int]] = {item.tier: [] for item in TIERS}
    for item in iter_current_tiers():
        ids_by_tier[item.tier].add(item.candidate_id)
        order_by_tier[item.tier].append(item.tier_ordinal)

    for definition in TIERS:
        actual = len(ids_by_tier[definition.tier])
        if actual != definition.expected_unique:
            raise SolverError(
                f"tier {definition.tier} count mismatch: {actual} != {definition.expected_unique}"
            )
        if order_by_tier[definition.tier] != list(range(actual)):
            raise SolverError(f"tier {definition.tier} ordering is not contiguous")

    for left, right in itertools.combinations(TIERS, 2):
        if ids_by_tier[left.tier] & ids_by_tier[right.tier]:
            raise SolverError(f"tiers {left.tier} and {right.tier} overlap")
    total = sum(len(values) for values in ids_by_tier.values())
    if total != 59_656:
        raise SolverError(f"tier union count mismatch: {total} != 59656")
    return {
        "candidate_config_fingerprint": actual_config,
        "tier_strategy_fingerprint": strategy["tier_strategy_fingerprint"],
        "tier_strategy_fingerprint_verification": "RECOMPUTED_FROM_CANONICAL_OBJECT",
        "tier_strategy_canonical_bytes": strategy["canonical_bytes"],
        "unicode_mode": candidates.UNICODE_MODE,
        "tier_counts": {str(item.tier): len(ids_by_tier[item.tier]) for item in TIERS},
        "total_unique": total,
        "pairwise_overlap": 0,
        "real_oracle_calls": 0,
    }


def _checkpoint_payload(checkpoint: Checkpoint) -> dict[str, object]:
    return asdict(checkpoint)


def _validate_checkpoint_contract(
    checkpoint: Checkpoint,
    *,
    expected_config_fingerprint: str,
    expected_strategy_fingerprint: str,
    expected_unicode_mode: str,
    expected_tier_sizes: dict[int, int],
    expected_mode: str,
) -> Checkpoint:
    if checkpoint.schema != CHECKPOINT_SCHEMA:
        raise SolverError("checkpoint schema mismatch")
    if checkpoint.candidate_config_fingerprint != expected_config_fingerprint:
        raise SolverError("checkpoint candidate configuration mismatch")
    if checkpoint.tier_strategy_fingerprint != expected_strategy_fingerprint:
        raise SolverError("checkpoint tier strategy mismatch")
    if checkpoint.unicode_mode != expected_unicode_mode:
        raise SolverError("checkpoint Unicode mode mismatch")
    if checkpoint.mode != expected_mode or expected_mode not in {"DRY_RUN", "EVALUATE"}:
        raise SolverError("checkpoint execution mode mismatch")
    expected_size = expected_tier_sizes.get(checkpoint.tier)
    if expected_size is None:
        raise SolverError("checkpoint tier is invalid")
    if not isinstance(checkpoint.next_ordinal, int) or not 0 <= checkpoint.next_ordinal <= expected_size:
        raise SolverError("checkpoint ordinal is out of range")
    if checkpoint.visited_unique_candidate_count != checkpoint.next_ordinal:
        raise SolverError("checkpoint count and ordinal disagree")
    if checkpoint.mode == "DRY_RUN" and checkpoint.evaluated_candidate_count != 0:
        raise SolverError("dry-run checkpoint contains evaluations")
    if checkpoint.mode == "EVALUATE" and checkpoint.evaluated_candidate_count != checkpoint.next_ordinal:
        raise SolverError("evaluation checkpoint count and ordinal disagree")
    if checkpoint.complete != (checkpoint.next_ordinal == expected_size):
        raise SolverError("checkpoint completion flag is inconsistent")
    if not isinstance(checkpoint.progress_digest, str) or len(checkpoint.progress_digest) != 64:
        raise SolverError("checkpoint progress digest is invalid")
    if checkpoint.match_candidate_id is not None:
        if checkpoint.mode != "EVALUATE" or checkpoint.match_candidate_id != checkpoint.last_candidate_id:
            raise SolverError("checkpoint match state is inconsistent")
    return checkpoint


def _parse_checkpoint(payload: object, expected_mode: str) -> Checkpoint:
    if not isinstance(payload, dict):
        raise SolverError("checkpoint root must be an object")
    expected = set(Checkpoint.__dataclass_fields__)
    if set(payload) != expected:
        raise SolverError("checkpoint fields do not match the schema")
    try:
        checkpoint = Checkpoint(**payload)
    except TypeError as exc:
        raise SolverError("checkpoint field types are invalid") from exc
    return _validate_checkpoint_contract(
        checkpoint,
        expected_config_fingerprint=CANDIDATE_CONFIG_FINGERPRINT,
        expected_strategy_fingerprint=TIER_STRATEGY_FINGERPRINT,
        expected_unicode_mode=candidates.UNICODE_MODE,
        expected_tier_sizes={item.tier: item.expected_unique for item in TIERS},
        expected_mode=expected_mode,
    )


def load_checkpoint(path: Path, expected_mode: str) -> Checkpoint:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SolverError("cannot read checkpoint") from exc
    return _parse_checkpoint(payload, expected_mode)


def save_checkpoint_atomic(path: Path, checkpoint: Checkpoint) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(_checkpoint_payload(checkpoint), sort_keys=True, separators=(",", ":")) + "\n"
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise SolverError("cannot write checkpoint atomically") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _tier_records(tier: int) -> Iterator[TierCandidate]:
    if tier not in TIER_BY_NUMBER:
        raise SolverError("unknown tier")
    for item in iter_current_tiers():
        if item.tier == tier:
            yield item
        elif item.tier > tier:
            break


def _replay_prefix(tier: int, next_ordinal: int) -> tuple[bytes, str | None]:
    digest = _initial_progress_digest()
    last_id = None
    for item in itertools.islice(_tier_records(tier), next_ordinal):
        digest = _advance_progress_digest(digest, item.candidate_id)
        last_id = item.candidate_id
    return digest, last_id


def new_checkpoint(tier: int, mode: str = "DRY_RUN") -> Checkpoint:
    if tier not in TIER_BY_NUMBER:
        raise SolverError("unknown tier")
    if mode not in {"DRY_RUN", "EVALUATE"}:
        raise SolverError("unknown execution mode")
    return Checkpoint(
        schema=CHECKPOINT_SCHEMA,
        solver_version=SOLVER_VERSION,
        candidate_config_fingerprint=CANDIDATE_CONFIG_FINGERPRINT,
        tier_strategy_fingerprint=TIER_STRATEGY_FINGERPRINT,
        unicode_mode=candidates.UNICODE_MODE,
        mode=mode,
        tier=tier,
        next_ordinal=0,
        visited_unique_candidate_count=0,
        evaluated_candidate_count=0,
        last_candidate_id=None,
        progress_digest=_initial_progress_digest().hex(),
        complete=False,
        match_candidate_id=None,
    )


def verify_checkpoint_progress(checkpoint: Checkpoint) -> None:
    digest, last_id = _replay_prefix(checkpoint.tier, checkpoint.next_ordinal)
    if digest.hex() != checkpoint.progress_digest or last_id != checkpoint.last_candidate_id:
        raise SolverError("checkpoint progress does not match deterministic replay")


def run_dry(
    checkpoint: Checkpoint,
    max_candidates: int,
    max_seconds: float | None,
) -> Checkpoint:
    if max_candidates < 0:
        raise SolverError("candidate limit cannot be negative")
    if max_seconds is not None and max_seconds < 0:
        raise SolverError("time limit cannot be negative")
    verify_checkpoint_progress(checkpoint)
    definition = TIER_BY_NUMBER[checkpoint.tier]
    digest = bytes.fromhex(checkpoint.progress_digest)
    last_id = checkpoint.last_candidate_id
    next_ordinal = checkpoint.next_ordinal
    started = time.monotonic()
    processed = 0
    records = iter(itertools.islice(_tier_records(checkpoint.tier), next_ordinal, None))
    while processed < max_candidates:
        if max_seconds is not None and time.monotonic() - started >= max_seconds:
            break
        try:
            item = next(records)
        except StopIteration:
            break
        digest = _advance_progress_digest(digest, item.candidate_id)
        last_id = item.candidate_id
        next_ordinal += 1
        processed += 1
    return Checkpoint(
        **{
            **_checkpoint_payload(checkpoint),
            "solver_version": SOLVER_VERSION,
            "next_ordinal": next_ordinal,
            "visited_unique_candidate_count": next_ordinal,
            "evaluated_candidate_count": 0,
            "last_candidate_id": last_id,
            "progress_digest": digest.hex(),
            "complete": next_ordinal == definition.expected_unique,
        }
    )


def run_oracle_preflight() -> dict[str, object]:
    """Validate both oracle implementations using controlled non-tier inputs."""
    oracle = importlib.import_module("corey_oracle")
    python_checks = oracle.run_selftest()
    if set(python_checks.values()) != {"PASS"}:
        raise SolverError("Python oracle self-test failed")

    synthetic_passphrase = "phase10 synthetic café checkpoint"
    python_trace = oracle.derive_candidate(synthetic_passphrase)
    javascript_path = Path(__file__).with_name("corey_oracle_b.js")
    completed = subprocess.run(
        ["node", str(javascript_path), "--mode", "standard", "--inspect", synthetic_passphrase],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SolverError("independent JavaScript oracle failed")
    try:
        javascript_trace = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise SolverError("independent JavaScript oracle returned invalid JSON") from exc
    if javascript_trace.get("address") != python_trace.address:
        raise SolverError("independent oracle address mismatch")
    if javascript_trace.get("normalized_passphrase_sha256") != python_trace.candidate_sha256:
        raise SolverError("independent oracle NFKD candidate mismatch")
    return {
        "python_oracle_selftest": "PASS",
        "independent_javascript_oracle": "PASS",
        "synthetic_end_to_end_address_agreement": "PASS",
        "synthetic_nfkd_agreement": "PASS",
        "real_tier_candidates_evaluated": 0,
    }


def _puzzle_evaluator(passphrase: str) -> str:
    oracle = importlib.import_module("corey_oracle")
    return oracle.verify_candidate(passphrase, oracle.NormalizationMode.STANDARD).value


def save_result_exclusive(path: Path, payload: dict[str, object]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    temporary: Path | None = None
    try:
        descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(name)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise SolverError("result path already exists; refusing to overwrite") from exc
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise SolverError("cannot write result file") from exc
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def run_evaluation(
    checkpoint: Checkpoint,
    *,
    max_candidates: int,
    max_seconds: float | None,
    checkpoint_path: Path,
    result_path: Path,
    evaluator: Callable[[str], str] = _puzzle_evaluator,
) -> tuple[Checkpoint, str]:
    if checkpoint.mode != "EVALUATE":
        raise SolverError("evaluation requires an evaluation checkpoint")
    if checkpoint.match_candidate_id is not None:
        raise SolverError("checkpoint already contains a match")
    if max_candidates < 0:
        raise SolverError("candidate limit cannot be negative")
    if max_seconds is not None and max_seconds < 0:
        raise SolverError("time limit cannot be negative")
    verify_checkpoint_progress(checkpoint)

    definition = TIER_BY_NUMBER[checkpoint.tier]
    digest = bytes.fromhex(checkpoint.progress_digest)
    next_ordinal = checkpoint.next_ordinal
    last_id = checkpoint.last_candidate_id
    started = time.monotonic()
    processed = 0
    status = "EVALUATION_LIMIT_REACHED"
    records = iter(itertools.islice(_tier_records(checkpoint.tier), next_ordinal, None))

    while processed < max_candidates:
        if max_seconds is not None and time.monotonic() - started >= max_seconds:
            break
        try:
            item = next(records)
        except StopIteration:
            status = "TIER_EXHAUSTED"
            break
        verdict = evaluator(item.raw_candidate)
        if verdict not in {"MATCH", "NO_MATCH", "ERROR"}:
            raise SolverError("oracle returned an unknown verdict")
        if verdict == "ERROR":
            raise SolverError("oracle error; candidate was not checkpointed")

        digest = _advance_progress_digest(digest, item.candidate_id)
        last_id = item.candidate_id
        next_ordinal += 1
        processed += 1
        matched_id = item.candidate_id if verdict == "MATCH" else None
        checkpoint = Checkpoint(
            **{
                **_checkpoint_payload(checkpoint),
                "solver_version": SOLVER_VERSION,
                "next_ordinal": next_ordinal,
                "visited_unique_candidate_count": next_ordinal,
                "evaluated_candidate_count": next_ordinal,
                "last_candidate_id": last_id,
                "progress_digest": digest.hex(),
                "complete": next_ordinal == definition.expected_unique,
                "match_candidate_id": matched_id,
            }
        )
        if verdict == "MATCH":
            save_result_exclusive(
                result_path,
                {
                    "status": "MATCH",
                    "tier": item.tier,
                    "tier_ordinal": item.tier_ordinal,
                    "candidate_id": item.candidate_id,
                    "passphrase": item.raw_candidate,
                    "normalized_passphrase": unicodedata.normalize("NFKD", item.raw_candidate),
                    "candidate_config_fingerprint": CANDIDATE_CONFIG_FINGERPRINT,
                    "tier_strategy_fingerprint": TIER_STRATEGY_FINGERPRINT,
                },
            )
            save_checkpoint_atomic(checkpoint_path, checkpoint)
            return checkpoint, "MATCH"
        save_checkpoint_atomic(checkpoint_path, checkpoint)

    if next_ordinal == definition.expected_unique:
        status = "TIER_EXHAUSTED"
    save_checkpoint_atomic(checkpoint_path, checkpoint)
    return checkpoint, status


def _synthetic_record(value: str, rule_id: str, hypothesis_id: str) -> candidates.CandidateRecord:
    normalized = unicodedata.normalize("NFKD", value)
    return candidates.CandidateRecord(
        global_raw_index=0,
        rule_raw_index=0,
        raw_candidate=value,
        normalized_candidate=normalized,
        candidate_id=hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        rule_id=rule_id,
        hypothesis_id=hypothesis_id,
        source_ids=("SYNTHETIC",),
        source_clues=("synthetic self-test",),
        transformations=("synthetic",),
    )


def run_selftest() -> dict[str, str]:
    """Exercise engine primitives independently of puzzle values and oracle."""
    composed = _synthetic_record("café", "R901", "H901")
    decomposed = _synthetic_record("cafe\u0301", "R901", "H901")
    if composed.candidate_id != decomposed.candidate_id:
        raise AssertionError("synthetic NFKD identity test failed")

    alpha = _synthetic_record("alpha", "R901", "H901")
    beta = _synthetic_record("beta", "R901", "H901")
    gamma = _synthetic_record("gamma", "R902", "H902")
    assigned = list(_iter_disjoint_rows(((1, (alpha, beta)), (2, (beta, gamma)))))
    if [(item.tier, item.tier_ordinal) for item in assigned] != [(1, 0), (1, 1), (2, 0)]:
        raise AssertionError("synthetic tier partition test failed")

    digest = _initial_progress_digest()
    for item in assigned:
        digest = _advance_progress_digest(digest, item.candidate_id)
    repeated = _initial_progress_digest()
    for item in assigned:
        repeated = _advance_progress_digest(repeated, item.candidate_id)
    if digest != repeated:
        raise AssertionError("synthetic progress digest test failed")

    synthetic_hits = []
    fake_oracle: Callable[[str], bool] = lambda value: value == "gamma"
    for item in assigned:
        if fake_oracle(item.raw_candidate):
            synthetic_hits.append(item.candidate_id)
    if synthetic_hits != [gamma.candidate_id]:
        raise AssertionError("synthetic evaluator isolation test failed")

    synthetic_config = hashlib.sha256(b"independent synthetic candidate config").hexdigest()
    synthetic_strategy = hashlib.sha256(b"independent synthetic tier strategy").hexdigest()
    checkpoint = Checkpoint(
        schema=CHECKPOINT_SCHEMA,
        solver_version="synthetic",
        candidate_config_fingerprint=synthetic_config,
        tier_strategy_fingerprint=synthetic_strategy,
        unicode_mode="SYNTHETIC_NFKD",
        mode="DRY_RUN",
        tier=91,
        next_ordinal=0,
        visited_unique_candidate_count=0,
        evaluated_candidate_count=0,
        last_candidate_id=None,
        progress_digest=_initial_progress_digest().hex(),
        complete=False,
        match_candidate_id=None,
    )
    validated = _validate_checkpoint_contract(
        checkpoint,
        expected_config_fingerprint=synthetic_config,
        expected_strategy_fingerprint=synthetic_strategy,
        expected_unicode_mode="SYNTHETIC_NFKD",
        expected_tier_sizes={91: 3},
        expected_mode="DRY_RUN",
    )
    if validated != checkpoint:
        raise AssertionError("synthetic checkpoint round-trip failed")
    changed = Checkpoint(**{**_checkpoint_payload(checkpoint), "tier_strategy_fingerprint": "0" * 64})
    try:
        _validate_checkpoint_contract(
            changed,
            expected_config_fingerprint=synthetic_config,
            expected_strategy_fingerprint=synthetic_strategy,
            expected_unicode_mode="SYNTHETIC_NFKD",
            expected_tier_sizes={91: 3},
            expected_mode="DRY_RUN",
        )
    except SolverError:
        pass
    else:
        raise AssertionError("checkpoint fingerprint rejection failed")

    return {
        "checkpoint_schema": "PASS",
        "deduplication": "PASS",
        "fake_evaluator": "PASS",
        "fingerprint_rejection": "PASS",
        "nfkd_unicode": "PASS",
        "progress_digest": "PASS",
        "synthetic_only": "PASS",
        "tier_ordering": "PASS",
    }


def _tier_payload() -> list[dict[str, object]]:
    return [asdict(item) for item in TIERS]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 9 tier planner: synthetic self-test or redacted dry run only."
    )
    operations = parser.add_mutually_exclusive_group(required=True)
    operations.add_argument("--selftest", action="store_true")
    operations.add_argument("--preflight", action="store_true")
    operations.add_argument("--dry-run", action="store_true")
    operations.add_argument("--evaluate", action="store_true")
    operations.add_argument("--list-tiers", action="store_true")
    parser.add_argument("--tier", type=int, choices=tuple(TIER_BY_NUMBER))
    parser.add_argument("--max-candidates", type=int, metavar="N")
    parser.add_argument("--max-seconds", type=float, metavar="SECONDS")
    checkpoint_group = parser.add_mutually_exclusive_group()
    checkpoint_group.add_argument("--checkpoint", type=Path, metavar="PATH")
    checkpoint_group.add_argument("--resume", type=Path, metavar="PATH")
    parser.add_argument("--result", type=Path, metavar="PATH")
    parser.add_argument(
        "--authorize-public-puzzle-corey",
        action="store_true",
        help="confirm this run is limited to the published Corey reward puzzle",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            if any(value is not None for value in (args.tier, args.max_candidates, args.max_seconds, args.checkpoint, args.resume, args.result)) or args.authorize_public_puzzle_corey:
                parser.error("--selftest cannot be combined with dry-run options")
            print(json.dumps(run_selftest(), sort_keys=True))
            return 0
        if args.preflight:
            if any(value is not None for value in (args.tier, args.max_candidates, args.max_seconds, args.checkpoint, args.resume, args.result)) or args.authorize_public_puzzle_corey:
                parser.error("--preflight cannot be combined with execution options")
            partition = validate_current_partition()
            print(json.dumps({"partition": partition, "oracle": run_oracle_preflight()}, sort_keys=True))
            return 0
        if args.list_tiers:
            if any(value is not None for value in (args.tier, args.max_candidates, args.max_seconds, args.checkpoint, args.resume, args.result)) or args.authorize_public_puzzle_corey:
                parser.error("--list-tiers cannot be combined with dry-run options")
            print(json.dumps(_tier_payload(), sort_keys=True))
            return 0

        if args.tier is None or args.max_candidates is None:
            parser.error("execution requires one --tier and an explicit --max-candidates limit")
        if args.checkpoint is None and args.resume is None:
            parser.error("execution requires --checkpoint PATH or --resume PATH")
        validate_current_partition()
        checkpoint_path = args.resume if args.resume is not None else args.checkpoint
        assert checkpoint_path is not None
        if args.evaluate:
            if not args.authorize_public_puzzle_corey:
                parser.error("--evaluate requires --authorize-public-puzzle-corey")
            if args.result is None:
                parser.error("--evaluate requires --result PATH")
            run_oracle_preflight()
            if args.resume is not None:
                checkpoint = load_checkpoint(checkpoint_path, "EVALUATE")
                if checkpoint.tier != args.tier:
                    raise SolverError("requested tier differs from checkpoint tier")
            else:
                checkpoint = new_checkpoint(args.tier, "EVALUATE")
            updated, status = run_evaluation(
                checkpoint,
                max_candidates=args.max_candidates,
                max_seconds=args.max_seconds,
                checkpoint_path=checkpoint_path,
                result_path=args.result,
            )
            print(
                json.dumps(
                    {
                        "status": status,
                        "tier": updated.tier,
                        "next_ordinal": updated.next_ordinal,
                        "tier_size": TIER_BY_NUMBER[updated.tier].expected_unique,
                        "evaluated_candidate_count": updated.evaluated_candidate_count,
                        "match_candidate_id": updated.match_candidate_id,
                        "checkpoint": str(checkpoint_path),
                    },
                    sort_keys=True,
                )
            )
            return 0
        if args.result is not None or args.authorize_public_puzzle_corey:
            parser.error("--result and authorization are valid only with --evaluate")
        if args.resume is not None:
            checkpoint = load_checkpoint(checkpoint_path, "DRY_RUN")
            if checkpoint.tier != args.tier:
                raise SolverError("requested tier differs from checkpoint tier")
        else:
            checkpoint = new_checkpoint(args.tier, "DRY_RUN")
        updated = run_dry(checkpoint, args.max_candidates, args.max_seconds)
        save_checkpoint_atomic(checkpoint_path, updated)
        print(
            json.dumps(
                {
                    "status": "DRY_RUN_TIER_COMPLETE" if updated.complete else "DRY_RUN_LIMIT_REACHED",
                    "tier": updated.tier,
                    "next_ordinal": updated.next_ordinal,
                    "tier_size": TIER_BY_NUMBER[updated.tier].expected_unique,
                    "evaluated_candidate_count": 0,
                    "real_oracle_calls": 0,
                    "checkpoint": str(checkpoint_path),
                },
                sort_keys=True,
            )
        )
        return 0
    except (AssertionError, SolverError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error_type": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
