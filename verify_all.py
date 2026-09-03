#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def shorten(part: str) -> str:
    """Render one argv element for display: no absolute paths from the runner's
    machine, and no dependence on where the repository happens to live."""
    if part == sys.executable:
        return "python3"
    try:
        return Path(part).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return part


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
        # Repository-relative, and flushed before the child runs: the previous
        # version printed absolute paths from the runner's filesystem, and
        # printed them after the output they were meant to introduce.
        shown = " ".join(shorten(part) for part in command)
        print("Running:", shown, flush=True)
        result = subprocess.run(command, cwd=ROOT)
        sys.stdout.flush()
        if result.returncode != 0:
            print("Verification failed for command:", shown, flush=True)
            return result.returncode
    print("All requested verification paths passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
