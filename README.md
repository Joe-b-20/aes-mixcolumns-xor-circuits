# Small XOR circuits for AES MixColumns

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21299092.svg)](https://doi.org/10.5281/zenodo.21299092)

This repository contains three explicit **2-input XOR circuits** for the AES
**MixColumns** linear transformation, together with self-contained verifiers.
Every circuit is a static, machine-checkable artifact. Nothing here depends on
how the circuits were found.

## The circuits

| File | Gates | Depth | Note |
|---|---|---|---|
| `circuits/mixcolumns_89gates.json` | **89** | 10 | Improves on the smallest published counts we are aware of: 91 (Lin, Xiang, Zeng, and Zhang, CT-RSA 2021) and 92 (Maximov). |
| `circuits/mixcolumns_98gates_depth3.json` | **98** | 3 | Improves on the 99-gate depth-3 point of Shi, Feng, and Xu. Depth 3 is the known minimum depth (see below). |
| `circuits/mixcolumns_91gates_depth6.json` | 91 | **6** | Matches the smallest published count (91) at depth 6; one gate fewer than Maximov's depth-6 92-gate circuit. |

The published comparison points, source-checked: the smallest XOR count we are
aware of is **91**, by Lin, Xiang, Zeng, and Zhang (CT-RSA 2021), stated in the
`s-XOR` (in-place) model. Because a `k`-instruction s-XOR program translates
instruction-for-gate into a `k`-gate 2-input XOR circuit, we use 91 — not just
Maximov's explicit 92-gate circuit — as the count to beat. Maximov's 92-gate,
depth-6 circuit remains the classic baseline stated directly in the 2-input-XOR
model used here, and the 99-gate depth-3 point is from Shi, Feng, and Xu (ToSC
2023). Yuan et al. (ToSC 2024) also report 91 XORs in an `s-XOR` /
quantum-depth framing. See **Claims and scope** below for the careful wording.

A depth note: the minimum depth of AES MixColumns in this model is 3, a known
fact stated e.g. by Shi, Feng, and Xu. It follows from the standard bound that
an output depending on `w` inputs needs depth at least `⌈log₂ w⌉`, and
MixColumns has outputs depending on 7 inputs. The depth-3 circuit above attains
this known minimum; its contribution is the gate count at that depth, not the
depth itself.

## The exact model

- A circuit is a list of **2-input XOR gates over GF(2)**.
- **Signals** are indexed from 0. Signals 0..31 are the 32 input bits.
- Gate `k` produces signal `32 + k`, whose value is
  `signal[gates[k][0]] XOR signal[gates[k][1]]`. Both parent indices are
  strictly smaller than the gate index, so the circuit is a DAG in list order.
- **Depth** of a signal = longest path in gates from any input; inputs have
  depth 0. Circuit depth = maximum over all gates.
- **Outputs**: `outputSignals[j]` names the signal carrying MixColumns output
  bit `j`, for `j = 0..31`.

### Bit / byte convention (this is the whole convention)

The AES state is four bytes `s0,s1,s2,s3`. Bit index `i` in 0..31 means bit
`(i mod 8)` of byte `(i div 8)`, least-significant-bit-first within each byte.
MixColumns maps input column `(a0,a1,a2,a3)` to the output column with
`out[c] = 2·a[c] ⊕ 3·a[(c+1)%4] ⊕ 1·a[(c+2)%4] ⊕ 1·a[(c+3)%4]`, with
multiplication in GF(2⁸) modulo `x⁸+x⁴+x³+x+1` (`0x11b`). This is the
standard forward MixColumns map from NIST FIPS 197-upd1, Section 5.1.3, Eq. 5.6.

The verifier rebuilds this specification from scratch, so the convention is not
just described in prose; it is executable. If your convention differs, such as a
different bit order or a transposed matrix, regenerate the target masks under
that convention before comparing counts.

## Verify

Pure Python 3, no dependencies:

~~~text
python3 verify_all.py
~~~

This runs the shipped software verification paths:

- `verify.py`: the lightweight repository verifier.
- `audit/cleanroom_verify.py`: a separate clean-room verifier that rebuilds AES
  MixColumns from an independent byte-level reference, recomputes metrics, runs
  deterministic random tests, and exercises adversarial rejection cases.

For a faster single-path check, you can still run:

~~~text
python3 verify.py
~~~

If Icarus Verilog is installed, you can also run the shipped hardware path:

~~~text
python3 verify_verilog.py
python3 verify_all.py --with-verilog
~~~

### Hardware (Verilog)

`verilog/<circuit>.v` is the netlist and `verilog/<circuit>_tb.v` is a testbench
that drives all 32 basis inputs and compares against the AES column masks.
`verify_verilog.py` automates all three shipped testbenches. For a single manual
run with Icarus Verilog:

~~~
cd verilog
iverilog -o sim.vvp mixcolumns_89gates.v mixcolumns_89gates_tb.v && vvp sim.vvp
~~~

Expected output includes `PASS: all 32 basis vectors correct`. The testbench
drives each unit input `e_i` and compares the output word against column
`i` of the MixColumns matrix: output bit `j` is set iff input `i` feeds
output `j`. This is the column, not row `T[j]`, because the matrix is not
symmetric.

## bounds.json

Machine-readable summary: for each circuit, `inputCount`, `gateCount`, `depth`,
`outputCount`, the `outputConvention` string, the exact
`sha256_circuit_json`, the exact `sha256_canonical_gates`, and additional
archival metadata.
`sha256_canonical_gates` is SHA-256 over the UTF-8 bytes of the compact JSON
string `{"inputCount":32,"gates":[...]}` with keys in that order. The rule is
implemented in `scripts/reproduce_canonical_hashes.py`. Both `verify.py` and
`audit/cleanroom_verify.py` recheck the circuit-file hash, the canonical gate
hash, and the declared gate/depth metadata.

## Claims and scope (please read)

We state results conservatively.

1. **Fewest we are aware of, not optimal.** We do **not** prove these gate
   counts are minimal. Minimality of XOR-circuit size, the Shortest Linear
   Program problem, is NP-hard and unproven for this matrix at the sizes here.
2. **Source-checked baselines.** The smallest previously published XOR count
   we are aware of is 91, by Lin, Xiang, Zeng, and Zhang (CT-RSA 2021), stated
   in the `s-XOR` (in-place) model. Every `k`-instruction s-XOR program yields
   a `k`-gate 2-input XOR circuit, so we compare against 91 rather than only
   against Maximov's explicit 92-gate 2-input-XOR circuit. The depth-3
   baseline is the 99-gate result of Shi, Feng, and Xu (ToSC 2023). Yuan et
   al. (ToSC 2024) likewise report 91 XORs in an `s-XOR` / quantum-depth
   framing. Gate counts and depths are invariant under input/output bit
   relabeling, so these comparisons do not depend on convention choices.
3. **Convention.** All counts are for the exact 2-input-XOR model and the
   exact MixColumns convention defined above. A hidden convention mismatch is
   the most common way such a comparison goes wrong, which is why the
   from-scratch verifier is included.
4. **Reproducibility of circuits vs. search.** The circuits in this folder are
   fully reproducible: anyone can re-run `verify.py` and confirm them forever.
   The discovery method is described elsewhere and is a separate, still
   developing line of work; none of the claims here depend on it.

## Contents

~~~
circuits/    three circuit JSON files
bounds.json  annotated summary + integrity metadata
verify.py    lightweight repository verifier
verify_all.py runs the repository verifier, clean-room verifier, and optional Verilog wrapper
verify_verilog.py compiles and runs all shipped Verilog testbenches when Icarus is available
scripts/     helper scripts for reproducing published metadata
audit/       clean-room verifier and its generated audit reports
verilog/     one netlist + one testbench per circuit
tests/       regression tests for shipped and malformed artifacts
PAPER.md     short write-up with conservative claims and caveats
paper/       LaTeX source of the ePrint note (appendices generated from circuits/)
~~~

## References

- National Institute of Standards and Technology, Advanced Encryption Standard
  (AES), NIST FIPS 197-upd1, May 9, 2023. DOI:
  <https://doi.org/10.6028/NIST.FIPS.197-upd1>
- Alexander Maximov, AES MixColumn with 92 XOR Gates, IACR ePrint 2019/833.
  <https://eprint.iacr.org/2019/833.pdf>
- Da Lin, Zejun Xiang, Xiangyong Zeng, and Shasha Zhang, A Framework to
  Optimize Implementations of Matrices, Topics in Cryptology – CT-RSA 2021,
  LNCS 12704, Springer, 2021. DOI:
  <https://doi.org/10.1007/978-3-030-75539-3_25>
- Haotian Shi, Xiutao Feng, and Shengyuan Xu, A Framework with Improved
  Heuristics to Optimize Low-Latency Implementations of Linear Layers, IACR
  Transactions on Symmetric Cryptology, 2023(4):489-510. DOI:
  <https://doi.org/10.46586/tosc.v2023.i4.489-510>
- Yufei Yuan, Wenling Wu, Tairong Shi, Lei Zhang, and Yu Zhang, A Framework to
  Improve the Implementations of Linear Layers, IACR Transactions on
  Symmetric Cryptology, 2024(2):322-347. DOI:
  <https://doi.org/10.46586/tosc.v2024.i2.322-347>

## License / citation

Released under MIT for archival reuse. If you use a circuit, please cite the
accompanying note (`PAPER.md`) and this repository via the archived DOI:
<https://doi.org/10.5281/zenodo.21299092> (see `CITATION.cff`).
