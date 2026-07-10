#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERILOG_DIR = ROOT / "verilog"
PASS_TOKEN = "PASS: all 32 basis vectors correct"


def discover_pairs() -> list[tuple[Path, Path]]:
    pairs = []
    for testbench in sorted(VERILOG_DIR.glob("*_tb.v")):
        netlist = VERILOG_DIR / testbench.name.replace("_tb.v", ".v")
        if not netlist.exists():
            raise FileNotFoundError(f"missing matching netlist for {testbench.name}: {netlist.name}")
        pairs.append((netlist, testbench))
    if not pairs:
        raise FileNotFoundError("no Verilog testbench pairs found")
    return pairs


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)


def missing_tools() -> list[str]:
    return [tool for tool in ("iverilog", "vvp") if shutil.which(tool) is None]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile and run all shipped Verilog testbenches.")
    parser.add_argument(
        "--allow-missing-tools",
        action="store_true",
        help="Exit successfully with a skip message instead of failing if Icarus Verilog is unavailable.",
    )
    args = parser.parse_args()

    missing = missing_tools()
    if missing:
        message = "Icarus Verilog is unavailable in PATH (" + ", ".join(missing) + " missing)."
        if args.allow_missing_tools:
            print(f"[SKIP] {message}")
            return 0
        print(f"[FAIL] {message} Install iverilog and vvp, or rerun with --allow-missing-tools.")
        return 1

    failures = 0
    with tempfile.TemporaryDirectory(prefix="mixcolumns-iverilog-") as tmpdir:
        build_dir = Path(tmpdir)
        for netlist, testbench in discover_pairs():
            output_path = build_dir / f"{netlist.stem}.vvp"
            compile_result = run_command(["iverilog", "-o", str(output_path), str(netlist), str(testbench)])
            if compile_result.returncode != 0:
                failures += 1
                print(f"[FAIL] {netlist.stem}: iverilog compile failed")
                if compile_result.stdout:
                    print(compile_result.stdout.rstrip())
                if compile_result.stderr:
                    print(compile_result.stderr.rstrip())
                continue

            sim_result = run_command(["vvp", str(output_path)])
            combined_output = chr(10).join(
                chunk for chunk in [sim_result.stdout.strip(), sim_result.stderr.strip()] if chunk
            )
            if sim_result.returncode != 0 or PASS_TOKEN not in sim_result.stdout:
                failures += 1
                print(f"[FAIL] {netlist.stem}: simulation did not report the expected PASS token")
                if combined_output:
                    print(combined_output)
                continue

            pass_line = next(
                (line.strip() for line in sim_result.stdout.splitlines() if PASS_TOKEN in line),
                PASS_TOKEN,
            )
            print(f"[ OK ] {netlist.stem}: {pass_line}")

    if failures:
        print(f"Verilog verification failed for {failures} circuit(s).")
        return 1

    print("All shipped Verilog testbenches passed under Icarus Verilog.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
