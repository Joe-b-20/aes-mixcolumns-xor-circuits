#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_COMMANDS = [
    [sys.executable, str(ROOT / "verify.py")],
    # No --update-artifacts: the clean-room verifier compares its recomputation
    # against the tracked audit files and writes nothing, so verifying never
    # dirties the working tree.
    [sys.executable, str(ROOT / "audit" / "cleanroom_verify.py")],
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the shipped verification entrypoints.")
    parser.add_argument(
        "--with-verilog",
        action="store_true",
        help="Also run verify_verilog.py. Requires iverilog and vvp unless --allow-missing-verilog is set.",
    )
    parser.add_argument(
        "--allow-missing-verilog",
        action="store_true",
        help="Only meaningful with --with-verilog. Skip the Verilog path instead of failing if Icarus is unavailable.",
    )
    args = parser.parse_args()

    commands = list(BASE_COMMANDS)
    if args.with_verilog:
        command = [sys.executable, str(ROOT / "verify_verilog.py")]
        if args.allow_missing_verilog:
            command.append("--allow-missing-tools")
        commands.append(command)

    for command in commands:
        print("Running:", " ".join(command))
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode != 0:
            print("Verification failed for command:", " ".join(command))
            return result.returncode
    print("All requested verification paths passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
