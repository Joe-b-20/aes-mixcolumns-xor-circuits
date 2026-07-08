# Small 2-input XOR circuits for AES MixColumns

*A short note accompanying the verified circuit artifacts in this repository.*

## Abstract

We report three explicit implementations of the AES MixColumns linear
transformation as circuits of 2-input XOR gates over GF(2): (i) an **89-gate**
circuit of unconstrained depth; (ii) a **98-gate** circuit of depth **3**; and
(iii) a **91-gate** circuit of depth **6**. To the best of our knowledge these
improve on, respectively, the smallest previously published 2-input-XOR counts of
91 (Yuan et al.) and 92 (Maximov) at unconstrained depth, and 99 (Shi, Feng, Xu,
ToSC 2023) at depth 3; and the 91-gate depth-6 circuit occupies a gate/depth
trade-off point not, as far as we are aware, previously reported. All three
circuits are provided as machine-checkable artifacts with a pure-Python verifier
that rebuilds the MixColumns specification from scratch. We make no optimality
claim.

## 1. Model and specification

A circuit is an ordered list of 2-input XOR gates. Signals `0..31` are the input
bits; gate `k` produces signal `32+k = signal[a] XOR signal[b]` with `a,b` both
strictly smaller than `32+k`. Depth counts gates on the longest input-to-signal
path (inputs at depth 0). The AES state and MixColumns matrix, and the exact
bit/byte convention, are fixed in `README.md` and, definitively, in `verify.py`,
which reconstructs the 32×32 GF(2) target map from the GF(2⁸) definition
(polynomial `0x11b`, column `[2,3,1,1]`). Because MixColumns is linear, agreement
on the 32 unit-input vectors is a **complete** correctness check.

## 2. Results

| Circuit | Gates | Depth | Comparison figure (published) |
|---|---|---|---|
| `mixcolumns_89gates` | 89 | 10 | 91 (Yuan et al.), 92 (Maximov) — unconstrained depth |
| `mixcolumns_98gates_depth3` | 98 | 3 | 99 (Shi, Feng, Xu, ToSC 2023) — depth 3 |
| `mixcolumns_91gates_depth6` | 91 | 6 | 91 at depth 8 (Yuan et al.); 92 at depth 6 (Maximov) |

The third circuit is worth isolating: at 91 gates it matches the smallest known
unconstrained count while having depth 6 rather than 8, and at depth 6 it uses one
fewer gate than the smallest depth-6 circuit we are aware of (Maximov, 92). It is
therefore not dominated by either neighbouring published point, and dominates
each of them in one coordinate at no cost in the other.

Each circuit is verified three independent ways: (a) `verify.py` against a
from-scratch GF(2⁸) MixColumns; (b) the Verilog testbenches against the 32 basis
responses; (c) a direct simulation of the emitted netlists. All three agree.

## 3. Honest scope

- **Not optimality.** Minimum 2-input-XOR circuit size (the Shortest Linear
  Program problem) is NP-hard; we do not prove any of these counts minimal. We
  claim only that they are the smallest we have found or seen published.
- **"Published best known."** Our comparison baselines are the best *published*
  2-input-XOR counts we located. We have not surveyed unpublished, patent, or
  hardware-library results; multiple-input-gate and technology-mapped results use
  a different cost model and are not directly comparable.
- **One convention.** All counts hold for the single, executable convention in
  `verify.py`. A different bit order or a transposed matrix is a different problem;
  re-derive the targets under your convention before comparing.
- **Circuits vs. method.** The artifacts here are self-contained and permanently
  reproducible. The discovery method is a separate, ongoing line of work and is
  deliberately out of scope for this note; none of the claims above rely on it.

## 4. Reproduce

```
python3 verify.py            # expects: ALL CIRCUITS VERIFIED.
```

## References (as located; verify before citing)

- H. Yuan et al., improved shortest-linear-program results for AES MixColumns
  (91 gates). *[bibliographic details to be confirmed by the reader]*
- A. Maximov, "AES MixColumn with 92 XOR gates," IACR ePrint 2019/833.
- H. Shi, X. Feng, S. Xu, "A Framework with Improved Heuristics to Optimize
  Low-Latency Implementations of Linear Layers," IACR ToSC 2023 (depth-3, 99
  gates).
