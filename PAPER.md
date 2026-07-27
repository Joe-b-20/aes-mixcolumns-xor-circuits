# Small 2-input XOR circuits for AES MixColumns

*A short note accompanying the verified circuit artifacts in this repository.
The typeset note is `paper/mixcolumns_note.pdf` (LaTeX source in `paper/`);
this file mirrors it.*

## Abstract

We report four explicit implementations of the AES MixColumns linear
transformation as circuits of 2-input XOR gates over GF(2). Three improve the
published depth–count Pareto frontier at their depth: (i) a **97-gate**
circuit at depth **3**, the known minimum depth, improving the 99-gate record
of Shi, Feng, and Xu (ToSC 2023); (ii) a **92-gate** circuit at depth **4**,
improving the 97-gate depth-4 point of Osvik and Canright (ePrint 2024/1076);
and (iii) an **89-gate** circuit at depth **5**, improving Osvik and
Canright's 94-gate depth-5 point by five gates and shallower than any
published circuit of fewer than 94 gates whose depth is stated. The fourth, an
**88-gate** circuit at depth **7**, **ties** the published gate-count floor
(Jean, ePrint 2026/1481, posted 2026-07-23, who has priority) with an
independent circuit sharing 61 of 88 internal masks; it does not beat it. A
fifth circuit, 88 gates at depth 8, is derived from Jean's and is dominated. No
87 was found: 47 canonical 88-gate circuits have exhaustively empty remove-≤3
neighbourhoods. All circuits are provided as machine-checkable artifacts with a
pure-Python verifier that rebuilds the MixColumns specification from scratch.
We make no optimality claim on gate counts.

## Corrections

Dated entries, in the same style as the Corrections section of `PRIOR_ART.md`.

- **2026-07-27 (version 2 of the note; supersedes the earlier 2026-07-27 entry
  made against version 1).** The note has been rewritten as **version 2** and
  now reports the two 88-gate circuits in its own Sections 2 and 4, so the
  earlier correction — which recorded that the version-1 results list was
  incomplete — no longer applies to the current text. It is restated here for
  the record rather than removed, and what it said still holds:
  - `mixcolumns_88gates_depth7` **matches** the published count floor — Jean's
    88 at depth 7, ePrint 2026/1481, posted 2026-07-23 — with an independent
    circuit (61 of 88 internal masks shared, Jaccard 0.530). It ties that
    point; it does not beat it, and Jean has priority.
  - `mixcolumns_88gates_depth8` is **derived from that published circuit**:
    its seed chain passes through Jean's 88. It is dominated by the depth-7
    circuit above (same count, greater depth) and improves nothing.
  - 97 @ 3, 92 @ 4 and 89 @ 5 remain on the depth–count Pareto frontier, and
    88 remains the published floor. See `README.md` and `PRIOR_ART.md`
    (Corrections).
  - Version 1 of the note (July 2026), which reported only the 97, 92 and
    89, stays archived at version DOI
    [10.5281/zenodo.21299093](https://doi.org/10.5281/zenodo.21299093). No
    claim of version 1 is withdrawn.

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

| Circuit | Gates | Depth | Published best at that depth | Relation |
|---|---|---|---|---|
| `mixcolumns_97gates_depth3` | 97 | 3 | 99 (Shi, Feng, Xu, ToSC 2023) | improves it by 2 |
| `mixcolumns_92gates_depth4` | 92 | 4 | 97 (Osvik, Canright, ePrint 2024/1076, App. G) | improves it by 5 |
| `mixcolumns_89gates_depth5` | 89 | 5 | 94 (Osvik, Canright, ePrint 2024/1076, App. F) | improves it by 5 |
| `mixcolumns_88gates_depth7` | 88 | 7 | 88 (Jean, ePrint 2026/1481) | **ties it, does not beat it** — an independent circuit at the same point (61/88 masks shared, Jaccard 0.530); Jean has priority |
| `mixcolumns_88gates_depth8` | 88 | 8 | — | **derived from Jean's 88** (its seed chain passes through it); dominated by the row above, so not a frontier point |

At unconstrained depth the published floor is 88 (Jean, ePrint 2026/1481);
Sun–Yang–Li's 89 (ePrint 2025/1493) states no depth. The project's earlier
circuits (89 @ depth 10, 98 @ depth 3, 91 @ depth 6) remain in the repository
for the archival record; each is dominated by a circuit above.

Three points are worth isolating. First, depth 3 is the known minimum depth for
AES MixColumns (stated e.g. by Shi, Feng, and Xu; it follows from the standard
bound that an output depending on w inputs needs depth at least ⌈log₂ w⌉, and
MixColumns has outputs of weight 7). The contribution of the 97-gate circuit
is therefore the gate count at that depth, not the depth itself. Second, the
89-gate depth-5 circuit is shallower than any published circuit of fewer
than 94 gates whose depth is stated; the published sub-89 point (88, Jean,
ePrint 2026/1481) sits at depth 7, so neither dominates the other and both
are on the frontier (Sun–Yang–Li's 89 states no depth). Third, the 88-gate
depth-7 circuit ties Jean's point rather than improving it: Jean's note was
posted 2026-07-23 and has priority, and the circuit here was found 2026-07-26
by this project's own search along its own logged lineage (from-scratch 97 @
depth 3 → 89 @ depth 6 → 89 @ depth 5 → a ρ²-symmetric 94 @ depth 5 → 88 @
depth 7), with no imported circuit anywhere in the chain.

Beyond the circuits, the note also reports machine-checked *local* certificates
for the 88-gate plateau: 47 canonical 88-gate circuits have exhaustively empty
remove-≤3 shells (so any 87 differs from each of them by ≥ 4 masks — this
project's own 88 @ depth 7 is *not* one of the 47); 105,801 of the ≈ 139,878
harvested distinct 88-gate mask sets are proven irreducible at k = 2; ≈ 165
million exact window decisions returned zero reducible windows; and every one
of the ≈ 139,878 has minimum depth ≥ 7, with 18,353 (13.1%) at exactly 7.
Windowed SAT (UNSAT to
k = 16 and k = 15 on two family anchors, 0 SAT anywhere) is evidence, not
proof — it is relative to the encoding's fixed slot order. None of this bounds
87 away globally.

Each circuit is verified by two shipped software paths: (a) `verify.py` against a
from-scratch GF(2^8) MixColumns; (b) `audit/cleanroom_verify.py` against a
separately written byte-level reference with deterministic random tests and
adversarial rejection checks. The Verilog testbenches provide an additional
simulation path when Icarus Verilog is available.

## 3. Honest scope

- **Not optimality.** Minimum 2-input-XOR circuit size, the Shortest Linear
  Program problem, is NP-hard; we do not prove any of these counts minimal,
  and the neighbourhood certificates above are local.
  We claim only that they are the smallest we have found or seen published.
- **Source-checked baselines.** The published depth–count frontier we compare
  against: 99 @ depth 3 (Shi, Feng, and Xu, ToSC 2023); 97 @ depth 4 and 94 @
  depth 5 (Osvik and Canright, ePrint 2024/1076, Appendices G and F); 92 @
  depth 6 (Maximov); and, at unconstrained depth, 89 (Sun–Yang–Li, ePrint
  2025/1493, depth not stated) and 88 @ depth 7 (Jean, ePrint 2026/1481).
  Earlier s-XOR baselines (91: Lin et al., CT-RSA 2021; Yuan et al., ToSC
  2024) are comparable because a k-instruction s-XOR program translates
  directly into a k-gate 2-input XOR circuit. We claim the smallest counts
  at depths 3, 4, and 5 — not at unconstrained depth. Results in other cost
  models (multi-input XOR gates, gate-equivalent area, quantum CNOT) are not
  comparable and are not claimed against; see `PRIOR_ART.md`, including its
  Corrections section. Gate counts and depths are invariant under bit
  relabeling, so these comparisons do not depend on convention choices. The
  depths quoted for Jean (7) and for Sun–Yang–Li (9) are this project's own
  measurements of its own transcriptions; neither paper states a depth.
- **Provenance.** 97 @ 3 and 92 @ 4 are from scratch; 89 @ 5 and 88 @ 7 are on
  this project's own lineage, rooted in a from-scratch 97 @ 3; **88 @ 8 is
  derived from published work** — its seed chain passes through Jean's 88
  (ePrint 2026/1481), which is credited wherever that circuit appears.
- **One convention.** All counts hold for the single executable convention in
  `verify.py`. A different bit order or a transposed matrix is a different
  problem; re-derive the targets under your convention before comparing.
- **Circuits vs. method.** The artifacts here are self-contained and
  permanently verifiable, and none of the claims depend on how the circuits
  were found. The search method (a value-set shortest-linear-program local
  search with plateau and hub moves) is published, with run evidence and
  reproduction instructions, at
  <https://github.com/Joe-b-20/slp-plateau-search>; see also Sections 3 and 4
  of the accompanying note (`paper/`). Reproduction times measured 2026-07-27
  with the shipped dependency-free Python, reported as measurements and not as
  promises, and with the shipped v2 engine: the from-scratch 97 @ depth 3 in
  81 s on one core; the 89 @ depth 5 in 19 s and 22 s from shipped seeds,
  against 592 s for the archived 2026-07-14 run on the v1 engine; the 88 @
  depth 7 in 19.4 and 31.0 minutes in two single-worker re-runs from the
  ρ²-symmetric 94 seed, against 32.9 minutes in the archived ten-worker run.
  The re-runs are re-runs, not independent confirmations.

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
- Yao Sun, Runhe Yang, and Ting Li, *Revisit the Boyar-Peralta Algorithm to
  Solve the Shortest Linear Program Problem*, IACR ePrint 2025/1493.
  <https://eprint.iacr.org/2025/1493>
- Jérémy Jean, *88-XOR Implementation of the AES MixColumns Matrix*, IACR
  ePrint 2026/1481. <https://eprint.iacr.org/2026/1481>
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
