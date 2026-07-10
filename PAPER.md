# Small 2-input XOR circuits for AES MixColumns

*A short note accompanying the verified circuit artifacts in this repository.*

## Abstract

We report three explicit implementations of the AES MixColumns linear
transformation as circuits of 2-input XOR gates over GF(2): (i) an **89-gate**
circuit of depth 10; (ii) a **98-gate** circuit of depth **3**; and (iii) a
**91-gate** circuit of depth **6**. The smallest previously published XOR
count we are aware of is 91, by Lin, Xiang, Zeng, and Zhang (CT-RSA 2021),
stated in the s-XOR model, whose programs translate instruction-for-gate into
2-input XOR circuits; the classic baseline stated directly in the 2-input-XOR
model is the 92-gate, depth-6 circuit of Maximov. The 89-gate circuit improves
on both. At depth 3, the 98-gate circuit improves on the 99-gate result of
Shi, Feng, and Xu (ToSC 2023), and depth 3 is the minimum possible depth for
this map. The 91-gate circuit matches the smallest published count while
achieving depth 6, one gate fewer than Maximov's depth-6 circuit. All three
circuits are provided as machine-checkable artifacts with a pure-Python
verifier that rebuilds the MixColumns specification from scratch. We make no
optimality claim on gate counts.

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

| Circuit | Gates | Depth | Comparison figure (published) |
|---|---|---|---|
| `mixcolumns_89gates` | 89 | 10 | 91 (Lin, Xiang, Zeng, Zhang, CT-RSA 2021, s-XOR); 92 (Maximov) |
| `mixcolumns_98gates_depth3` | 98 | 3 | 99 (Shi, Feng, Xu, ToSC 2023) — depth 3 |
| `mixcolumns_91gates_depth6` | 91 | 6 | 92 at depth 6 (Maximov); ties the 91 count of Lin et al. |

Two points are worth isolating. First, depth 3 is optimal: every MixColumns
output depends on at least 5 input bits, a depth-d circuit of 2-input gates
depends on at most 2^d inputs, so depth 2 is impossible, and the 98-gate
circuit attains depth 3. Second, the 91-gate depth-6 circuit matches the
smallest published gate count while using one gate fewer than Maximov's
depth-6 circuit; we include it as an explicit shallow trade-off point between
the 89-gate result and the depth-3 98-gate result.

Each circuit is verified by two shipped software paths: (a) `verify.py` against a
from-scratch GF(2^8) MixColumns; (b) `audit/cleanroom_verify.py` against a
separately written byte-level reference with deterministic random tests and
adversarial rejection checks. The Verilog testbenches provide an additional
simulation path when Icarus Verilog is available.

## 3. Honest scope

- **Not optimality.** Minimum 2-input-XOR circuit size, the Shortest Linear
  Program problem, is NP-hard; we do not prove any of these counts minimal.
  We claim only that they are the smallest we have found or seen published.
- **Source-checked baselines.** The smallest previously published XOR count
  we are aware of is 91, by Lin, Xiang, Zeng, and Zhang (CT-RSA 2021), stated
  in the s-XOR (in-place) model. A k-instruction s-XOR program translates
  directly into a k-gate 2-input XOR circuit, so we compare against 91 rather
  than only against Maximov's explicit 92-gate circuit. The depth-3 baseline
  is the 99-gate result of Shi, Feng, and Xu (ToSC 2023). Yuan et al. (ToSC
  2024) likewise report 91 XORs in an s-XOR / quantum-depth framing. Gate
  counts and depths are invariant under bit relabeling, so these comparisons
  do not depend on convention choices.
- **One convention.** All counts hold for the single executable convention in
  `verify.py`. A different bit order or a transposed matrix is a different
  problem; re-derive the targets under your convention before comparing.
- **Circuits vs. method.** The artifacts here are self-contained and
  permanently reproducible. The discovery method is a separate, ongoing line
  of work and is deliberately out of scope for this note.

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
