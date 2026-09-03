from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import audit.cleanroom_verify as cv

ROOT = Path(__file__).resolve().parents[1]
BASE_CIRCUIT_PATH = ROOT / "circuits" / "mixcolumns_89gates_depth10.json"


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

    def test_listings_match_artifacts(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_listings.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_verilog_matches_artifacts(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_verilog.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_adhoc_accepts_a_circuit_with_no_bounds_entry(self) -> None:
        """A stranger's correct circuit must verify. Default mode requires a
        bounds.json entry (check 4); --adhoc is the path for everyone else."""
        artifact = copy.deepcopy(self.base_circuit)
        artifact["id"] = "mixcolumns_someone_else"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "newcomer.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "verify.py"), "--adhoc", str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ALL CIRCUITS CORRECT", result.stdout)
        self.assertNotIn("bounds.json does not match", result.stdout)

        # ... and the same file in default mode is still refused, because the
        # shipped set is exactly the set this repository makes claims about.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "newcomer.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "verify.py"), str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)

    def test_adhoc_still_rejects_every_bad_circuit(self) -> None:
        bad = sorted((ROOT / "tests" / "bad").glob("*.json"))
        self.assertEqual(len(bad), 8)
        for path in bad:
            with self.subTest(mutant=path.name):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "verify.py"), "--adhoc", str(path)],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0, msg=result.stdout)
                self.assertIn("[FAIL]", result.stdout)

    def test_adhoc_verifies_the_shipped_prior_art(self) -> None:
        """Jean's and Sun-Yang-Li's transcribed circuits are not records of
        this project, are absent from bounds.json, and are verified this way."""
        files = sorted((ROOT / "prior_art").glob("*.json"))
        self.assertEqual(len(files), 2)
        result = subprocess.run(
            [sys.executable, str(ROOT / "verify.py"), "--adhoc"] + [str(f) for f in files],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("ALL CIRCUITS CORRECT", result.stdout)

    def test_prior_art_is_excluded_from_the_records(self) -> None:
        bounds_ids = {
            entry["id"]
            for entry in json.loads((ROOT / "bounds.json").read_text(encoding="utf-8"))["circuits"]
        }
        self.assertEqual(len(bounds_ids), len(list((ROOT / "circuits").glob("*.json"))))
        for path in sorted((ROOT / "prior_art").glob("*.json")):
            artifact = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn(artifact.get("id"), bounds_ids)
            self.assertNotIn(path.stem, bounds_ids)

    def test_generated_data_files_match_their_generators(self) -> None:
        """matrix.txt, golden_vectors.txt, wrong_answers.md,
        circuits_metadata.csv and docs/frontier.svg are generated, not typed.
        Each generator's --check mode must find the shipped file
        byte-identical, so a file and the script that vouches for it cannot
        drift apart."""
        for script in (
            "build_matrix.py",
            "build_golden_vectors.py",
            "build_wrong_answers.py",
            "build_metadata.py",
            "generate_frontier_svg.py",
        ):
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / script), "--check"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
                self.assertIn("[OK]", result.stdout)
                self.assertNotIn("[STALE]", result.stdout)

    def test_no_documentation_cites_a_file_that_does_not_exist(self) -> None:
        """The audit found three phantom tool references. This closes the door."""
        phantom = ("_build_wrong.py", "CONTROLS.txt", "verify_circuit.py")
        checked = 0
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".txt", ".json", ".py", ".cff"}:
                continue
            if ".git" in path.parts or "__pycache__" in path.parts:
                continue
            # prior_art/ holds other people's circuits, kept byte-for-byte as
            # imported; their own outputConvention text names the *method*
            # repository's verify_circuit.py, and prior_art/README.md says so.
            # Editing an imported artifact is not an option.
            if path.parent.name == "prior_art":
                continue
            # ... and this file, which has to name the phantoms to forbid them.
            if path.resolve() == Path(__file__).resolve():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            checked += 1
            for name in phantom:
                self.assertNotIn(
                    name,
                    text,
                    msg=f"{path.relative_to(ROOT)} cites {name}, which this repository does not ship",
                )
        self.assertGreater(checked, 20)

    def test_rejects_permuted_outputs(self) -> None:
        artifact = copy.deepcopy(self.base_circuit)
        artifact["outputSignals"][0], artifact["outputSignals"][1] = artifact["outputSignals"][1], artifact["outputSignals"][0]
        self.assert_rejected(artifact, "permuted outputs")


if __name__ == "__main__":
    unittest.main()
