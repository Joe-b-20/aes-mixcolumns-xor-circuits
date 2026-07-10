#!/usr/bin/env python3
"""Generate human-readable plain-text listings in listings/ from circuits/*.json.

Each listing states the convention, the canonical SHA-256 from bounds.json,
one line per gate (s{32+k} = s{a} ^ s{b}), and the output-signal map
(y{j} = s{outputSignals[j]}). Never edit the .txt files by hand; regenerate
them from the JSON artifacts. --check exits nonzero if any listing on disk
differs from what the artifacts produce.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LISTINGS_DIR = REPO_ROOT / "listings"


def render(circuit: dict, bounds_entry: dict) -> str:
    lines = []
    lines.append(f"# {circuit['id']}: AES MixColumns, {circuit['gateCount']} two-input XOR gates, depth {circuit['depth']}.")
    lines.append("# Generated from circuits/%s.json by scripts/generate_listings.py; do not edit." % circuit["id"])
    lines.append("# Convention: s0..s31 are the input bits; bit i is bit (i mod 8) of state byte")
    lines.append("# (i div 8), least-significant-bit first. y0..y31 are the MixColumns output bits")
    lines.append("# under the same numbering (NIST FIPS 197-upd1, Sec. 5.1.3, Eq. 5.6, poly 0x11b).")
    lines.append(f"# Canonical gate-list SHA-256: {bounds_entry['sha256_canonical_gates']}")
    lines.append("")
    for k, (a, b) in enumerate(circuit["gates"]):
        lines.append(f"s{32 + k} = s{a} ^ s{b}")
    lines.append("")
    for j, s in enumerate(circuit["outputSignals"]):
        lines.append(f"y{j} = s{s}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit nonzero if listings on disk are stale.")
    args = parser.parse_args()

    bounds = {
        e["id"]: e
        for e in json.loads((REPO_ROOT / "bounds.json").read_text(encoding="utf-8"))["circuits"]
    }
    stale = []
    LISTINGS_DIR.mkdir(exist_ok=True)
    for path in sorted((REPO_ROOT / "circuits").glob("*.json")):
        circuit = json.loads(path.read_text(encoding="utf-8"))
        text = render(circuit, bounds[circuit["id"]])
        out_path = LISTINGS_DIR / f"{circuit['id']}.txt"
        if args.check:
            if not out_path.exists() or out_path.read_text(encoding="utf-8") != text:
                stale.append(out_path.name)
        else:
            out_path.write_text(text, encoding="utf-8")
            print(f"wrote listings/{out_path.name}")

    if args.check:
        if stale:
            print("stale listings (regenerate with scripts/generate_listings.py): " + ", ".join(stale))
            return 1
        print("listings match the circuit artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
