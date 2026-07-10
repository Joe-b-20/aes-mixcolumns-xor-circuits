#!/usr/bin/env python3
"""Reproduce the sha256_canonical_gates values stored in bounds.json."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def canonical_blob(gates: list[list[int]]) -> bytes:
    """Match the original publish generator: compact JSON of inputCount + gates."""
    return json.dumps(
        {"inputCount": 32, "gates": gates},
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def load_bounds(repo_root: Path) -> dict[str, dict]:
    bounds = json.loads((repo_root / "bounds.json").read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in bounds["circuits"]}


def iter_circuits(repo_root: Path) -> list[tuple[str, dict]]:
    circuits_dir = repo_root / "circuits"
    rows = []
    for path in sorted(circuits_dir.glob("*.json")):
        rows.append((path.stem, json.loads(path.read_text(encoding="utf-8"))))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--check-bounds",
        action="store_true",
        help="Exit nonzero if any reproduced hash differs from bounds.json.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of plain text.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    bounds = load_bounds(repo_root)
    rows = []
    ok = True

    for circuit_id, circuit in iter_circuits(repo_root):
        actual = sha256_hex(canonical_blob(circuit["gates"]))
        expected = bounds.get(circuit_id, {}).get("sha256_canonical_gates")
        matches = actual == expected
        ok &= matches
        rows.append(
            {
                "id": circuit_id,
                "sha256_canonical_gates": actual,
                "bounds_value": expected,
                "matches_bounds": matches,
            }
        )

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            suffix = " [OK]" if row["matches_bounds"] else " [MISMATCH]"
            print(f"{row['id']}: {row['sha256_canonical_gates']}{suffix}")

    return 0 if (not args.check_bounds or ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
