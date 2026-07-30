#!/usr/bin/env python3
"""Generate the Verilog netlists and testbenches in verilog/ from circuits/*.json.

For each circuit this writes `verilog/<id>.v`, a flat netlist of 2-input XOR
`assign` statements, and `verilog/<id>_tb.v`, a testbench that drives all 32 unit
inputs and compares each response against the corresponding column of the
MixColumns matrix. The expected columns are not read from the circuit: they are
rebuilt from the GF(2^8) specification via verify.mixcolumns_target_masks(), so
the testbench checks the circuit against the spec rather than against itself.

Never edit the .v files by hand; regenerate them from the JSON artifacts.
--check exits nonzero if any file on disk differs from what the artifacts
produce, and writes nothing (it is how the tracked netlists are shown to be a
pure function of circuits/).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERILOG_DIR = REPO_ROOT / "verilog"

sys.path.insert(0, str(REPO_ROOT))
import verify  # noqa: E402  (the repository verifier, used only for the spec)


def matrix_columns() -> list[int]:
    """col[i] is the 32-bit output word produced by the unit input e_i."""
    spec = verify.mixcolumns_target_masks()
    columns = []
    for input_bit in range(32):
        word = 0
        for output_bit in range(32):
            if (spec[output_bit] >> input_bit) & 1:
                word |= 1 << output_bit
        columns.append(word)
    return columns


def render_netlist(circuit: dict) -> str:
    cid = circuit["id"]
    gates = circuit["gates"]
    top = 32 + len(gates) - 1
    lines = [
        f"// AES MixColumns, {circuit['gateCount']} two-input XOR gates, "
        f"depth {circuit['depth']}. Auto-generated; do not edit.",
        f"module {cid}(input [31:0] x, output [31:0] y);",
        f"  wire [{top}:0] s;",
        "  assign s[31:0] = x;",
    ]
    for k, (a, b) in enumerate(gates):
        lines.append(f"  assign s[{32 + k}] = s[{a}] ^ s[{b}];")
    for j, s in enumerate(circuit["outputSignals"]):
        lines.append(f"  assign y[{j}] = s[{s}];")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


def render_testbench(circuit: dict, columns: list[int]) -> str:
    cid = circuit["id"]
    lines = [
        "// Exhaustive linear test: for each unit input e_i, check y equals column i",
        "// of the MixColumns matrix (output bit j set iff input i feeds output j).",
        f"module {cid}_tb;",
        "  reg [31:0] x; wire [31:0] y; integer i, fails;",
        "  reg [31:0] col [0:31];",
        f"  {cid} dut(.x(x), .y(y));",
        "  initial begin",
        "    fails = 0;",
    ]
    for i, word in enumerate(columns):
        lines.append(f"    col[{i}] = 32'h{word:08x};")
    lines += [
        "    for (i = 0; i < 32; i = i + 1) begin",
        "      x = (32'h1 << i);",
        "      #1;",
        '      if (y !== col[i]) begin $display("FAIL input bit %0d: got %h expected %h", '
        "i, y, col[i]); fails = fails + 1; end",
        "    end",
        f'    if (fails == 0) $display("PASS: all 32 basis vectors correct — '
        f'{circuit["gateCount"]} gates, depth {circuit["depth"]}");',
        '    else $display("FAILED: %0d mismatches", fails);',
        "    $finish;",
        "  end",
        "endmodule",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit nonzero if any file on disk is stale.")
    args = parser.parse_args()

    columns = matrix_columns()
    stale = []
    VERILOG_DIR.mkdir(exist_ok=True)
    for path in sorted((REPO_ROOT / "circuits").glob("*.json")):
        circuit = json.loads(path.read_text(encoding="utf-8"))
        for name, text in ((f"{circuit['id']}.v", render_netlist(circuit)),
                           (f"{circuit['id']}_tb.v", render_testbench(circuit, columns))):
            out_path = VERILOG_DIR / name
            if args.check:
                if not out_path.exists() or out_path.read_text(encoding="utf-8") != text:
                    stale.append(name)
            else:
                out_path.write_text(text, encoding="utf-8")
                print(f"wrote verilog/{name}")

    if args.check:
        if stale:
            print("stale Verilog (regenerate with scripts/generate_verilog.py): " + ", ".join(stale))
            return 1
        print("Verilog matches the circuit artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
