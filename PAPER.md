# Small 2-input XOR circuits for AES MixColumns

*A short note accompanying the verified circuit artifacts in this repository.*

## Abstract

We report three explicit implementations of the AES MixColumns linear
transformation as circuits of 2-input XOR gates over GF(2) that improve the
entire published depth–count Pareto frontier: (i) a **97-gate** circuit at
depth **3**, the known minimum depth, improving the 99-gate record of Shi,
Feng, and Xu (ToSC 2023); (ii) a **92-gate** circuit at depth **4**, improving
the 97-gate depth-4 point of Osvik and Canright (ePrint 2024/1076); and (iii)
an **89-gate** circuit at depth **5** — the smallest XOR count we are aware of
at any depth — improving Osvik and Canright's 94-gate depth-5 point by five
gates and the smallest published count in any comparable model (91, Lin,
Xiang, Zeng, and Zhang, CT-RSA 2021, s-XOR) by two. All circuits are provided
as machine-checkable artifacts with a pure-Python verifier that rebuilds the
MixColumns specification from scratch. We make no optimality claim on gate
counts.

## 1. Model and specification

A circuit is an ordered list of 2-input XOR gates. Signals `0..31` are the input
bits; gate `k` produces signal `32+k = signal[a] XOR signal[b]` with `a,b` both
strictly smaller than `32+k`. Depth counts gates on the longest input-to-signal
path, with inputs at depth 0. The AES state, MixColumns matrix, and exact
bit/byte convention are fixed in `README.md` and, definitively, in
`verify.py`, which reconstructs the 32×32 GF(2) target map from the GF(2⁸)
definition (polynomial `0x11b`, column `[2,3,1,1]`) following NIST FIPS
197-upd1, Section 5.1.3, Eq. 5.6. Because MixColumns is linear, agreement on
the 32 unit-input vectors is a complete correctness check.

## 2. Results

| Circuit | Gates | Depth | Published best at that depth |
|---|---|---|---|
| `mixcolumns_97gates_depth3` | 97 | 3 | 99 (Shi, Feng, Xu, ToSC 2023) |
| `mixcolumns_92gates_depth4` | 92 | 4 | 97 (Osvik, Canright, ePrint 2024/1076, App. G) |
| `mixcolumns_89gates_depth5` | 89 | 5 | 94 (Osvik, Canright, ePrint 2024/1076, App. F); smallest published count at any depth: 91 (Lin et al., CT-RSA 2021, s-XOR) |

The project's earlier circuits (89 @ depth 10, 98 @ depth 3, 91 @ depth 6)
remain in the repository for the archival record; each is dominated by a
circuit above.

Two points are worth isolating. First, depth 3 is the known minimum depth for
AES MixColumns (stated e.g. by Shi, Feng, and Xu; it follows from the standard
bound that an output depending on w inputs needs depth at least ⌈log₂ w⌉, and
MixColumns has outputs of weight 7). The contribution of the 97-gate circuit
is therefore the gate count at that depth, not the depth itself. Second, the
89-gate depth-5 circuit Pareto-dominates every published point: it has fewer
gates than the smallest published count at any depth (91) and lower depth than
every published circuit of fewer than 94 gates.

Each circuit is verified by two shipped software paths: (a) `verify.py` against a
from-scratch GF(2^8) MixColumns; (b) `audit/cleanroom_verify.py` against a
separately written byte-level reference with deterministic random tests and
adversarial rejection checks. The Verilog testbenches provide an additional
simulation path when Icarus Verilog is available.

## 3. Honest scope

- **Not optimality.** Minimum 2-input-XOR circuit size, the Shortest Linear
  Program problem, is NP-hard; we do not prove any of these counts minimal.
  We claim only that they are the smallest we have found or seen published.
- **Source-checked baselines.** The published depth–count frontier we compare
  against: 99 @ depth 3 (Shi, Feng, and Xu, ToSC 2023); 97 @ depth 4 and 94 @
  depth 5 (Osvik and Canright, ePrint 2024/1076, Appendices G and F); 92 @
  depth 6 (Maximov); and 91 @ depth 7 (Lin, Xiang, Zeng, and Zhang, CT-RSA
  2021, s-XOR — a k-instruction s-XOR program translates directly into a
  k-gate 2-input XOR circuit, so we treat it as comparable). Yuan et al.
  (ToSC 2024) likewise report 91 XORs in an s-XOR / quantum-depth framing.
  Results in other cost models (multi-input XOR gates, gate-equivalent area,
  quantum CNOT) are not comparable and are not claimed against; see
  `PRIOR_ART.md`. Gate counts and depths are invariant under bit relabeling,
  so these comparisons do not depend on convention choices.
- **One convention.** All counts hold for the single executable convention in
  `verify.py`. A different bit order or a transposed matrix is a different
  problem; re-derive the targets under your convention before comparing.
- **Circuits vs. method.** The artifacts here are self-contained and
  permanently verifiable, and none of the claims depend on how the circuits
  were found. The search method (a value-set shortest-linear-program local
  search with plateau and hub moves) is published, with run evidence and
  reproduction instructions, at
  <https://github.com/Joe-b-20/slp-plateau-search>; see also Section 3 of the
  accompanying note (`paper/`).

## 4. Reproduce

~~~text
python3 verify_all.py
~~~

This runs the shipped software verification paths. For the faster
repository-only check, run `python3 verify.py`.

If Icarus Verilog is installed, the shipped hardware-verification path can be
run with `python3 verify_verilog.py` or included in the combined entrypoint with
`python3 verify_all.py --with-verilog`.

For canonical-hash metadata reproduction, also run
`python3 scripts/reproduce_canonical_hashes.py --check-bounds`.

## References

- National Institute of Standards and Technology, *Advanced Encryption Standard
  (AES)*, NIST FIPS 197-upd1, May 9, 2023. DOI:
  <https://doi.org/10.6028/NIST.FIPS.197-upd1>
- Alexander Maximov, *AES MixColumn with 92 XOR Gates*, IACR ePrint 2019/833.
  <https://eprint.iacr.org/2019/833.pdf>
- Dag Arne Osvik and David Canright, *A More Compact AES, and More*, IACR
  ePrint 2024/1076. <https://eprint.iacr.org/2024/1076>
- Da Lin, Zejun Xiang, Xiangyong Zeng, and Shasha Zhang, *A Framework to
  Optimize Implementations of Matrices*, Topics in Cryptology – CT-RSA 2021,
  LNCS 12704, Springer, 2021. DOI:
  <https://doi.org/10.1007/978-3-030-75539-3_25>
- Haotian Shi, Xiutao Feng, and Shengyuan Xu, *A Framework with Improved
  Heuristics to Optimize Low-Latency Implementations of Linear Layers*, IACR
  Transactions on Symmetric Cryptology, 2023(4):489-510. DOI:
  <https://doi.org/10.46586/tosc.v2023.i4.489-510>
- Yufei Yuan, Wenling Wu, Tairong Shi, Lei Zhang, and Yu Zhang, *A Framework to
  Improve the Implementations of Linear Layers*, IACR Transactions on
  Symmetric Cryptology, 2024(2):322-347. DOI:
  <https://doi.org/10.46586/tosc.v2024.i2.322-347>
