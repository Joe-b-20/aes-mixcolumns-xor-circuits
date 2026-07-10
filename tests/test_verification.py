from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import audit.cleanroom_verify as cv

ROOT = Path(__file__).resolve().parents[1]
BASE_CIRCUIT_PATH = ROOT / "circuits" / "mixcolumns_89gates.json"


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.target_masks = cv.build_target_masks()
        cls.base_circuit = json.loads(BASE_CIRCUIT_PATH.read_text(encoding="utf-8"))

    def assert_rejected(self, artifact: dict, label: str) -> None:
        ok, issues = cv.validate_artifact(artifact, self.target_masks)
        self.assertFalse(ok, msg=f"{label} unexpectedly passed: {issues}")
        self.assertTrue(issues, msg=f"{label} produced no rejection reason")

    def test_verify_py_passes(self) -> None:
        result = subprocess.run([sys.executable, str(ROOT / "verify.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ALL CIRCUITS VERIFIED.", result.stdout)

    def test_verify_all_passes(self) -> None:
        result = subprocess.run([sys.executable, str(ROOT / "verify_all.py")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("All requested verification paths passed.", result.stdout)

    def test_verify_all_with_optional_verilog_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "verify_all.py"), "--with-verilog", "--allow-missing-verilog"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("All requested verification paths passed.", result.stdout)

    def test_verify_verilog_path(self) -> None:
        command = [sys.executable, str(ROOT / "verify_verilog.py")]
        have_iverilog = shutil.which("iverilog") is not None and shutil.which("vvp") is not None
        if not have_iverilog:
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Icarus Verilog is unavailable in PATH", result.stdout)
            skipped = subprocess.run(command + ["--allow-missing-tools"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(skipped.returncode, 0, msg=skipped.stdout + skipped.stderr)
            self.assertIn("[SKIP]", skipped.stdout)
            return

        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("All shipped Verilog testbenches passed under Icarus Verilog.", result.stdout)

    def test_rejects_wrong_gatecount(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        artifact["gateCount"] += 1
        self.assert_rejected(artifact, "wrong gate count")

    def test_rejects_missing_output_signals(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        del artifact["outputSignals"]
        self.assert_rejected(artifact, "missing outputSignals")

    def test_rejects_forward_reference(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        artifact["gates"][0] = [0, 9999]
        self.assert_rejected(artifact, "forward reference")

    def test_rejects_dead_gate(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        artifact["gates"].append([0, 1])
        artifact["gateCount"] += 1
        self.assert_rejected(artifact, "dead gate")

    def test_rejects_wrong_depth(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        artifact["depth"] += 1
        self.assert_rejected(artifact, "wrong depth")

    def test_rejects_permuted_outputs(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        artifact["outputSignals"][0], artifact["outputSignals"][1] = artifact["outputSignals"][1], artifact["outputSignals"][0]
        self.assert_rejected(artifact, "permuted outputs")


if __name__ == "__main__":
    unittest.main()
