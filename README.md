# Small XOR circuits for AES MixColumns

This repository contains three explicit **2-input XOR circuits** for the AES
**MixColumns** linear transformation, together with self-contained verifiers.
Every circuit is a static, machine-checkable artifact. Nothing here depends on
how the circuits were found.

## The circuits

| File | Gates | Depth | Note |
|---|---|---|---|
| `circuits/mixcolumns_89gates.json` | **89** | 10 | Fewest 2-input XOR gates we are aware of (any depth). |
| `circuits/mixcolumns_98gates_depth3.json` | **98** | 3 | Fewest 2-input XOR gates we are aware of at depth 3. |
| `circuits/mixcolumns_91gates_depth6.json` | 91 | **6** | A distinct gate/depth trade-off point (see below). |

For reference, the figures we compare against are 91 gates (Yuan et al.) and 92
gates (Maximov) at unconstrained depth, and 99 gates at depth 3 (Shi, Feng and
Xu, ToSC 2023). See **Claims and scope** below for the careful wording.

## The exact model

- A circuit is a list of **2-input XOR gates over GF(2)**.
- **Signals** are indexed from 0. Signals `0..31` are the 32 input bits.
- Gate `k` (`k = 0, 1, ...`) produces signal `32 + k`, whose value is
  `signal[gates[k][0]] XOR signal[gates[k][1]]`. **Both parent indices are
  strictly smaller** than the gate's own index (the circuit is a DAG in list
  order; no feedback).
- **Depth** of a signal = longest path (in gates) from any input; inputs have
  depth 0. Circuit depth = maximum over all gates.
- **Outputs**: `outputSignals[j]` names the signal carrying MixColumns output
  bit `j`, for `j = 0..31`.

### Bit / byte convention (this is the whole convention — there is no other)

The AES state is 4 bytes `s0,s1,s2,s3`. **Bit index `i` (0..31) is bit `(i mod 8)`
of byte `(i div 8)`, least-significant-bit-first within each byte.** MixColumns
maps input column `(a0,a1,a2,a3)` to the output column with
`out[c] = 2·a[c] ⊕ 3·a[(c+1)%4] ⊕ 1·a[(c+2)%4] ⊕ 1·a[(c+3)%4]`, multiplication in
GF(2⁸) modulo `x⁸+x⁴+x³+x+1` (`0x11b`).

**The verifier rebuilds this specification from scratch**, so the convention is
not a claim you must trust — it is executable. If your convention differs (e.g.
MSB-first, or a transposed matrix), a circuit that is correct here may read as
incorrect under your convention, and vice versa; regenerate the target masks
under your convention and re-check. This is the one place a reader must be
careful, and the verifier makes it explicit.

## Verify

Pure Python 3, no dependencies:

```
python3 verify.py
```

It rebuilds AES MixColumns in GF(2⁸), then for each circuit checks: every gate is
a 2-input XOR of earlier signals; the declared outputs equal the 32 MixColumns
output bits (a linear map is fully determined by its action on the 32 basis
inputs, so this is a **complete** check, not a sample); the reported gate count
and depth match the gate list; and the SHA-256 in `bounds.json` matches the file
on disk. Expected final line: `ALL CIRCUITS VERIFIED.`

### Hardware (Verilog)

`verilog/<circuit>.v` is the netlist; `verilog/<circuit>_tb.v` is a testbench that
drives all 32 basis inputs and compares against the AES column masks. With Icarus
Verilog:

```
cd verilog
iverilog -o sim.vvp mixcolumns_89gates.v mixcolumns_89gates_tb.v && vvp sim.vvp
```

Expected: `PASS: all 32 basis vectors correct`.

## `bounds.json`

Machine-readable summary: for each circuit, `inputCount`, `gateCount`, `depth`,
`outputCount`, the `outputConvention` string, two SHA-256 hashes (over the
canonical gate list and over the circuit JSON file as written), and the verified
properties. `verify.py` re-derives and re-checks all of it.

## Claims and scope (please read)

We state results conservatively.

1. **"Fewest we are aware of," not "optimal."** We do **not** prove these gate
   counts are minimal. Minimality of XOR-circuit size (the Shortest Linear
   Program problem) is NP-hard and unproven for this matrix at the sizes here.
2. **"Best known" vs "published best known."** Our comparison figures (91, 92, 99)
   are the best *published* counts we found. We have not exhaustively surveyed
   unpublished or hardware-specific results, and multiple-input-gate or
   technology-mapped results are a **different cost model** and not comparable.
3. **Convention.** All counts are for the exact 2-input-XOR model and the exact
   MixColumns convention defined above. A hidden convention mismatch is the most
   common way such a comparison goes wrong; the from-scratch verifier is included
   precisely to remove it.
4. **Reproducibility of the circuits vs. of the search.** The **circuits** in this
   folder are fully reproducible: anyone can re-run `verify.py` and confirm them
   forever. The **method** that discovered them is described elsewhere and is a
   separate, still-developing line of work; none of the claims here depend on it.

## Contents

```
circuits/    three circuit JSON files
bounds.json  annotated summary + SHA-256
verify.py    pure-Python, zero-dependency verifier (the specification)
verilog/     one netlist + one testbench per circuit
PAPER.md     short write-up with the conservative claims
```

## License / citation

Released for archival (e.g. Zenodo) and reuse. If you use a circuit, please cite
the accompanying note (`PAPER.md`) and this repository.
