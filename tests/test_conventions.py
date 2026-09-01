"""The normative data files must agree with the specification verify.py rebuilds.

`matrix.txt`, `matrix.sha256` and `golden_vectors.txt` are the conventions
section of the README as data. If any of them drifted away from the map the
verifier actually checks against, every circuit here would still verify and the
documentation would silently be wrong about what they compute. These tests
close that gap.
"""
from __future__ import annotations

import hashlib
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import verify  # noqa: E402


def apply_map(masks: list[int], x: int) -> int:
    """Apply the 32x32 map given as output masks to a 32-bit input vector."""
    out = 0
    for j, m in enumerate(masks):
        if bin(m & x).count("1") & 1:
            out |= 1 << j
    return out


def bytes_to_vector(bs: list[int]) -> int:
    v = 0
    for i, b in enumerate(bs):
        v |= b << (8 * i)
    return v


class ConventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = verify.mixcolumns_target_masks()

    def test_matrix_sha256_matches_the_file(self) -> None:
        raw = (ROOT / "matrix.txt").read_bytes()
        declared = (ROOT / "matrix.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(hashlib.sha256(raw).hexdigest(), declared)

    def test_matrix_txt_is_the_map_the_verifier_checks(self) -> None:
        rows = [r for r in (ROOT / "matrix.txt").read_text(encoding="utf-8").split() if r]
        self.assertEqual(len(rows), 32, "matrix.txt must have 32 rows")
        for r in rows:
            self.assertEqual(len(r), 32, "each row must have 32 columns")
        # row r, column c set  <=>  output bit r depends on input bit c
        for r, row in enumerate(rows):
            mask = 0
            for c, ch in enumerate(row):
                self.assertIn(ch, "01", "matrix.txt must be 0/1 characters")
                if ch == "1":
                    mask |= 1 << c
            self.assertEqual(
                mask,
                self.spec[r],
                f"matrix.txt row {r} = {mask:#010x}, spec says {self.spec[r]:#010x}",
            )

    def test_golden_vectors_are_produced_by_the_spec(self) -> None:
        text = (ROOT / "golden_vectors.txt").read_text(encoding="utf-8")
        pairs = re.findall(
            r"in  bytes : ([0-9a-f ]+)\n\s*out bytes : ([0-9a-f ]+)", text
        )
        self.assertGreaterEqual(len(pairs), 3, "expected several golden vectors")
        for ins, outs in pairs:
            xb = [int(t, 16) for t in ins.split()]
            yb = [int(t, 16) for t in outs.split()]
            self.assertEqual(len(xb), 4)
            self.assertEqual(len(yb), 4)
            got = apply_map(self.spec, bytes_to_vector(xb))
            self.assertEqual(
                got,
                bytes_to_vector(yb),
                f"{ins.strip()} -> expected {outs.strip()}, spec gives {got:#010x}",
            )

    def test_the_fips197_worked_example_is_present(self) -> None:
        text = (ROOT / "golden_vectors.txt").read_text(encoding="utf-8")
        self.assertIn("db 13 53 45", text)
        self.assertIn("8e 4d a1 bc", text)


if __name__ == "__main__":
    unittest.main()
