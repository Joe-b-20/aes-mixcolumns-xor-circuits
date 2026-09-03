#!/usr/bin/env python3
"""Shared plumbing for the four scripts/build_*.py generators.

Every normative data file in this repository is generated, not typed. Each
generator takes no input but the repository's own circuits and the
specification `verify.py` rebuilds from GF(2^8), writes exactly one file, and
prints the controls it ran while doing so. With --check it writes nothing and
exits nonzero if the file on disk is not what it would have written, which is
what CI and tests/ use: the shipped file and its generator cannot drift apart.
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def parse_args(what: str) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=f"Generate {what}.")
    ap.add_argument(
        "--check",
        action="store_true",
        help="Write nothing; exit nonzero if the file on disk differs from what "
             "this script would generate.",
    )
    return ap.parse_args()


def emit(rel: str, body: bytes, check: bool) -> int:
    """Write `body` to ROOT/rel, or compare against it under --check."""
    path = ROOT / rel
    if not check:
        path.write_bytes(body)
        print(f"wrote {rel}  ({len(body)} bytes)")
        return 0

    if not path.exists():
        print(f"[STALE] {rel} does not exist")
        return 1
    on_disk = path.read_bytes()
    if on_disk == body:
        print(f"[OK] {rel} is byte-identical to what {Path(sys.argv[0]).name} generates")
        return 0
    print(f"[STALE] {rel} differs from what {Path(sys.argv[0]).name} generates")
    diff = difflib.unified_diff(
        on_disk.decode("utf-8", "replace").splitlines(),
        body.decode("utf-8", "replace").splitlines(),
        fromfile=f"{rel} (on disk)",
        tofile=f"{rel} (generated)",
        lineterm="",
    )
    for i, line in enumerate(diff):
        if i > 40:
            print("  ...")
            break
        print("  " + line)
    return 1
