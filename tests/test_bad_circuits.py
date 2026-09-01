"""Every file in tests/bad/ must be rejected by verify.py, for the right reason.

A verifier that cannot say no is worthless, so each mutant carries exactly one
defect and this module asserts that the verifier names *that* defect — not
merely that it complained about something.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAD = ROOT / "tests" / "bad"
sys.path.insert(0, str(ROOT))

import verify  # noqa: E402


# file stem -> a substring that must appear in at least one reported problem
EXPECTED = {
    "bad_removed_gate": "invalid signal index",
    "bad_modified_parent_pair": "expected",
    "bad_permuted_output_bindings": "expected",
    "bad_reversed_output_bindings": "expected",
    "bad_incorrect_depth_metadata": "depth",
    "bad_incorrect_gatecount_metadata": "gateCount",
    "bad_forward_reference": "non-earlier signal",
    "bad_missing_output_signals": "outputSignals",
}


class BadCircuitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = verify.mixcolumns_target_masks()
        cls.bounds = {
            e["id"]: e
            for e in json.loads((ROOT / "bounds.json").read_text(encoding="utf-8"))["circuits"]
        }

    def test_every_bad_file_is_covered(self) -> None:
        on_disk = {p.stem for p in BAD.glob("*.json")}
        self.assertEqual(on_disk, set(EXPECTED), "tests/bad/ and EXPECTED disagree")
        self.assertTrue(on_disk, "tests/bad/ is empty")

    def test_the_good_circuit_still_passes(self) -> None:
        """The control: the unmutated circuit these came from must verify."""
        path = ROOT / "circuits" / "mixcolumns_88gates_depth5.json"
        _, gates, depth, problems = verify.verify_circuit(str(path), self.spec, self.bounds)
        self.assertEqual(problems, [], "the record circuit must verify cleanly")
        self.assertEqual((gates, depth), (88, 5))

    def test_bad_circuits_are_rejected(self) -> None:
        for stem, needle in sorted(EXPECTED.items()):
            with self.subTest(circuit=stem):
                _, _, _, problems = verify.verify_circuit(
                    str(BAD / f"{stem}.json"), self.spec, self.bounds
                )
                # Every mutant carries an id of its own, so "no matching entry
                # in bounds.json" is expected and is not the defect under test.
                real = [p for p in problems if "bounds.json" not in p]
                self.assertTrue(real, f"{stem}: no defect reported at all")
                self.assertTrue(
                    any(needle in p for p in real),
                    f"{stem}: expected a problem mentioning {needle!r}, got {real}",
                )


if __name__ == "__main__":
    unittest.main()
