# Small XOR circuits for AES MixColumns

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21299092.svg)](https://doi.org/10.5281/zenodo.21299092)
[![verify](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml/badge.svg)](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml)

Verified 2-input XOR circuits for AES MixColumns. Three improve the published
depth–count Pareto frontier: **97 gates at depth 3** (the minimum possible
depth), **92 at depth 4**, **89 at depth 5**. A fourth, **88 at depth 7**,
*matches, and does not beat*, the published count floor — Jean, ePrint
2026/1481, who has priority — with an independent circuit. The floor is 88 and
stays 88.

Every circuit is a static artifact checked by a verifier that rebuilds the
MixColumns specification from scratch; no claim here depends on how the
circuits were found. Source-by-source audit of every comparison:
[`PRIOR_ART.md`](PRIOR_ART.md).

## Verify

Pure Python 3, no dependencies:

~~~text
python3 verify_all.py
~~~

This runs both shipped software paths over every file in `circuits/`:

- `verify.py`, the lightweight repository verifier;
- `audit/cleanroom_verify.py`, a separate clean-room verifier that rebuilds
  MixColumns from an independent byte-level reference, recomputes metrics, runs
  deterministic random tests, and exercises adversarial rejection cases.

A passing run prints one line per circuit and ends in `ALL CIRCUITS VERIFIED.`

~~~text
[ OK ] mixcolumns_88gates_depth7: 88 gates, depth 7 — all 32 outputs correct, SHA fields match
~~~

`python3 verify.py` alone is the faster single-path check. With Icarus Verilog
installed, `python3 verify_all.py --with-verilog` adds the hardware path
(`verify_verilog.py` on its own runs the testbenches only).

`audit/recomputed_metrics.json` and `audit/MATHEMATICAL_VERIFICATION.md` are
always generated, never hand-written: by default the clean-room run recomputes
them, compares against the tracked copies, reports match or mismatch and writes
nothing (so verifying leaves the tree clean); `python3
audit/cleanroom_verify.py --update-artifacts` is what regenerates them.

### Hardware (Verilog)

`verilog/<circuit>.v` is the netlist and `verilog/<circuit>_tb.v` a testbench
driving all 32 basis inputs. For a single manual run:

~~~
cd verilog
iverilog -o sim.vvp mixcolumns_89gates_depth5.v mixcolumns_89gates_depth5_tb.v && vvp sim.vvp
~~~

Expected output includes `PASS: all 32 basis vectors correct`. The testbench
drives each unit input `e_i` and compares the output word against column `i` of
the MixColumns matrix: output bit `j` is set iff input `i` feeds output `j`.
This is the column, not row `T[j]`, because the matrix is not symmetric.

## The circuits

| File | Gates | Depth | Published best at that depth | Status |
|---|---|---|---|---|
| `circuits/mixcolumns_97gates_depth3.json` | 97 | **3** | 99 (Shi, Feng, and Xu, ToSC 2023) | improves it by 2 |
| `circuits/mixcolumns_92gates_depth4.json` | 92 | **4** | 97 (Osvik and Canright, ePrint 2024/1076, App. G) | improves it by 5 |
| `circuits/mixcolumns_89gates_depth5.json` | **89** | **5** | 94 (Osvik and Canright, ePrint 2024/1076, App. F) | improves it by 5 |
| `circuits/mixcolumns_88gates_depth7.json` | 88 | 7 | 88 (Jean, ePrint 2026/1481, posted 2026-07-23; the paper states no depth — 7 is our measurement of our transcription) | **matches it, does not beat it** — an independent circuit at the same point (61/88 shared masks, Jaccard 0.530); Jean has priority |

A second 88-gate circuit ships alongside them and is **not** a frontier point:

| File | Gates | Depth | Status |
|---|---|---|---|
| `circuits/mixcolumns_88gates_depth8.json` | 88 | 8 | **Derived from published work**: its seed chain passes through Jean's 88 (ePrint 2026/1481) — ρ²-symmetrized and peeled to 95, orbit-walked to 92, then unioned with a 91 of this project's own lineage before the descent. A third distinct construction by mask overlap (Jaccard 0.455 to Jean's 88, 0.544 to the 88 @ depth 7), but dominated by that 88 @ depth 7 — same count, greater depth — so it improves nothing. |

Earlier circuits from this project, kept for the archival record, each now
dominated by a circuit above:

| File | Gates | Depth | Superseded by |
|---|---|---|---|
| `circuits/mixcolumns_98gates_depth3.json` | 98 | 3 | 97 @ depth 3 |
| `circuits/mixcolumns_91gates_depth6.json` | 91 | 6 | 89 @ depth 5 |
| `circuits/mixcolumns_89gates_depth10.json` | 89 | 10 | 89 @ depth 5 |

These v1 circuits came from earlier, more primitive versions of the same
search, whose exact code state was not preserved; what is and is not
reconstructable about their provenance is documented in
[METHODS.md, "The earlier (v1) circuits"](https://github.com/Joe-b-20/slp-plateau-search/blob/main/METHODS.md#the-earlier-v1-circuits).
No current claim depends on them.

Each circuit is also a human-readable plain-text listing in `listings/`
(`s32 = s15 ^ s23`, one gate per line, generated by
`scripts/generate_listings.py`).

![The published depth–count Pareto frontier for AES MixColumns vs this work](docs/frontier.svg)

The published frontier in comparable models, source-checked in `PRIOR_ART.md`:
**99 @ depth 3** (Shi, Feng, and Xu, ToSC 2023), **97 @ depth 4** and **94 @
depth 5** (Osvik and Canright, ePrint 2024/1076), **92 @ depth 6** (Maximov,
ePrint 2019/833; also Xiang et al., ToSC 2020, s-XOR), and **88 @ depth 7**
(Jean, ePrint 2026/1481, which supersedes Lin et al.'s 91 at that depth and, as
the count floor, Sun–Yang–Li's 89 of ePrint 2025/1493). Neither Jean nor
Sun–Yang–Li states a depth; where this repository needs one — the figure
above, the frontier table in `PRIOR_ART.md` — it uses **7** and **9**
respectively, this project's own measurements of its own transcriptions, not
figures from the papers. The 89 @
depth 5 here is shallower than any published circuit of fewer than 94 gates
whose depth is stated.

Depth 3 is the known minimum depth for this map, a fact stated e.g. by Shi,
Feng, and Xu: an output depending on `w` inputs needs depth at least
`⌈log₂ w⌉`, and MixColumns has outputs depending on 7 inputs. The 97-gate
circuit attains that minimum; its contribution is the count at that depth, not
the depth.

## The exact model

- A circuit is a list of **2-input XOR gates over GF(2)**.
- **Signals** are indexed from 0. Signals 0..31 are the 32 input bits.
- Gate `k` produces signal `32 + k`, whose value is
  `signal[gates[k][0]] XOR signal[gates[k][1]]`. Both parent indices are
  strictly smaller than `32 + k`, so the circuit is a DAG in list order.
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

The verifier rebuilds this specification from scratch, so the convention is
executable, not just prose. If your convention differs — a different bit order,
a transposed matrix — regenerate the target masks under it before comparing
counts.

## bounds.json

Machine-readable summary: per circuit, `inputCount`, `gateCount`, `depth`,
`outputCount`, `outputConvention`, `sha256_circuit_json`,
`sha256_canonical_gates`, a `claim` string stating exactly what is and is not
asserted, and for the two 88-gate circuits a `provenance` string recording the
lineage. The circuit JSON files carry only the eight schema keys the verifiers
require; provenance lives beside them because no correctness claim depends on
it.

`sha256_canonical_gates` is SHA-256 over the UTF-8 bytes of the compact JSON
string `{"inputCount":32,"gates":[...]}` with keys in that order, implemented in
`scripts/reproduce_canonical_hashes.py`. Both verifiers recheck the circuit-file
hash, the canonical gate hash, and the declared gate/depth metadata.

## Claims and scope

1. **Fewest we are aware of, not optimal.** We do **not** prove these counts
   minimal. Minimality of XOR-circuit size — the Shortest Linear Program
   problem — is NP-hard and unproven for this matrix at these sizes.
2. **Comparability.** Every `k`-instruction s-XOR (in-place) program yields a
   `k`-gate 2-input XOR circuit, so s-XOR counts are comparable and the earlier
   91s (Lin et al., CT-RSA 2021; Yuan et al., ToSC 2024) are in scope. Other
   cost models — multi-input XOR gates, gate-equivalent area, quantum CNOT — are
   not, and are not claimed against. Gate counts and depths are invariant under
   input/output bit relabeling, so no comparison here depends on convention.
3. **Scope of the count claims.** We claim the smallest counts at depths 3, 4,
   and 5 — not at unconstrained depth, where the published floor is Jean's 88.
   Our 88 @ depth 7 ties that floor and does not beat it (Jean has priority);
   our 88 @ depth 8 is derived from it and dominated. See the tables above and
   `PRIOR_ART.md`, Claim 4.
4. **Convention.** All counts are for the exact model and convention defined
   above. A hidden convention mismatch is the most common way such a comparison
   goes wrong, which is why the from-scratch verifier is included.
5. **Circuits vs. search.** The search method — a value-set
   shortest-linear-program local search with plateau and hub moves — is
   published separately in
   [`slp-plateau-search`](https://github.com/Joe-b-20/slp-plateau-search), with
   the method write-up, untouched run archives, machine-checked
   local-optimality certificates, and per-record reproduction instructions. The
   two 88-gate circuits come from its **v2.0.0** release.

## Contents

~~~
circuits/    eight circuit JSON files (see the tables above)
listings/    the same circuits as human-readable plain text (generated)
docs/        generated figures (the depth-count frontier chart)
PRIOR_ART.md source-by-source audit of every comparison claim
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
- Dag Arne Osvik and David Canright, A More Compact AES, and More, IACR
  ePrint 2024/1076. <https://eprint.iacr.org/2024/1076>
- Yao Sun, Runhe Yang, and Ting Li, Revisit the Boyar-Peralta Algorithm to
  Solve the Shortest Linear Program Problem, IACR ePrint 2025/1493.
  <https://eprint.iacr.org/2025/1493>
- Jérémy Jean, 88-XOR Implementation of the AES MixColumns Matrix, IACR
  ePrint 2026/1481. <https://eprint.iacr.org/2026/1481>
- Da Lin, Zejun Xiang, Xiangyong Zeng, and Shasha Zhang, A Framework to
  Optimize Implementations of Matrices, Topics in Cryptology – CT-RSA 2021,
  LNCS 12704, Springer, 2021. DOI:
  <https://doi.org/10.1007/978-3-030-75539-3_25>
- Zejun Xiang, Xiangyong Zeng, Da Lin, Zhenzhen Bao, and Shasha Zhang,
  Optimizing Implementations of Linear Layers, IACR Transactions on Symmetric
  Cryptology, 2020(2):120-145. DOI:
  <https://doi.org/10.13154/tosc.v2020.i2.120-145>
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
accompanying note ([`paper/mixcolumns_note.pdf`](paper/mixcolumns_note.pdf);
`PAPER.md` is the short markdown version) and this repository via the
archived DOI: <https://doi.org/10.5281/zenodo.21299092> (see `CITATION.cff`).
