# Small 2-input XOR circuits for AES MixColumns

*A short note accompanying the verified circuit artifacts in this repository.
The typeset note, `paper/mixcolumns_note.pdf` (LaTeX source in `paper/`), is
the authoritative version; this file is a condensed markdown companion.*

## Abstract

We report seven explicit implementations of the AES MixColumns linear
transformation as circuits of 2-input XOR gates over GF(2). Four improve the
published depth–count Pareto frontier at their depth, on lineages that contain
no imported circuit: (i) a **97-gate** circuit at depth **3**, the known minimum
depth, improving the 99-gate record of Shi, Feng, and Xu (ToSC 2023); (ii) a
**92-gate** circuit at depth **4**, improving the 97-gate depth-4 point of Osvik
and Canright (ePrint 2024/1076); (iii) an **89-gate** circuit at depth **5**,
improving Osvik and Canright's 94-gate depth-5 point by five gates and shallower
than any published circuit of fewer than 94 gates whose depth is stated; and
(iv) an **88-gate** circuit at depth **6**, four gates below the published
depth-6 point (92, Maximov) and one level shallower than the published 88 at the
same count. That 88 is **not a new gate count**: 88 is the published floor, held
by Jean (ePrint 2026/1481, posted 2026-07-23), **who has priority**. A fifth
circuit, 88 gates at depth **7**, **ties** that floor with an independent circuit
sharing 61 of 88 internal masks; it does not beat it. Two further 88s, at depths
**5** and **8**, are **derived from Jean's circuit** and reported as derived work;
the depth-5 one is six gates below the published depth-5 point. Combined
frontier: **97 @ 3, 92 @ 4, 88 @ 5**; with no imported material anywhere in the
lineage: **97 @ 3, 92 @ 4, 89 @ 5, 88 @ 6**. No 87 was found: 47 canonical
88-gate circuits have exhaustively empty remove-≤3 neighbourhoods, as does the
new 88 at depth 6. All circuits are machine-checkable artifacts with a
pure-Python verifier that rebuilds the MixColumns specification from scratch. We
make no optimality claim on gate counts.

## Corrections

Dated entries, in the style of the Corrections section of `PRIOR_ART.md`.

- **2026-07-29 (note version 3).** Adds two 88-gate circuits, at depths 6 and 5,
  in Sections 2 and 4. The depth-6 one is from scratch on its own lineage; the
  depth-5 one is **derived from Jean's published 88** and is labelled so wherever
  it appears. No claim of version 1 or 2 is withdrawn, but one **observation** of
  version 2 is now refuted by these circuits and is corrected here and in
  Section 2: version 2 recorded that "no 88-gate mask set of minimum build depth
  ≤ 6 has been seen in this harvesting". Two have now been seen, at depths 6 and
  5. It was reported as an observation and not as a certified claim, and the
  certified negative result nearby is a narrower one that still stands: no 88 at
  depth 6 exists near the *old* 88-plateau (all 4,861 two-critical cores UNSAT at
  cap 6). Both new circuits live in a different basin, so that certificate is not
  contradicted. A second consequence: version 2 observed that the
  best-certified 88-gate shells and this project's only Jean-independent 88 were
  disjoint sets; with the depth-6 circuit's remove-≤3 shell now exhaustively
  empty, they are not.
- **2026-07-27 (note version 2).** Version 1 of this note (July 2026) reported
  only the 97, 92 and 89; version 2 adds the two 88-gate circuits, in Sections
  2 and 4. No claim of version 1 is withdrawn; version 1 remains available in
  the repository history and in the Zenodo version archive under the concept
  DOI [10.5281/zenodo.21299092](https://doi.org/10.5281/zenodo.21299092).

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

| Circuit | Gates | Depth | Published best at that depth | Relation | Lineage |
|---|---|---|---|---|---|
| `mixcolumns_97gates_depth3` | 97 | 3 | 99 (Shi, Feng, Xu, ToSC 2023) | improves it by 2 | own |
| `mixcolumns_92gates_depth4` | 92 | 4 | 97 (Osvik, Canright, ePrint 2024/1076, App. G) | improves it by 5 | own |
| `mixcolumns_89gates_depth5` | 89 | 5 | 94 (Osvik, Canright, ePrint 2024/1076, App. F) | improves it by 5 | own |
| `mixcolumns_88gates_depth5` | 88 | 5 | 94 (as above) | improves it by 6, but **derived**, and not a new count | **derived from Jean's 88** |
| `mixcolumns_88gates_depth6` | 88 | 6 | 92 (Maximov, ePrint 2019/833; also Xiang et al., ToSC 2020, s-XOR) | improves it by 4, and dominates the published 88 — same count, one level shallower. **Not a new count**: 88 is Jean's, who has priority | own |
| `mixcolumns_88gates_depth7` | 88 | 7 | 88 (Jean, ePrint 2026/1481) | **ties it, does not beat it** — an independent circuit at the same point (61/88 masks shared, Jaccard 0.530); Jean has priority. Dominated by the row above | own |
| `mixcolumns_88gates_depth8` | 88 | 8 | — | **derived from Jean's 88** (its seed chain passes through it); dominated, so not a frontier point | **derived from Jean's 88** |

Two frontiers follow, and both are reported: **97 @ 3, 92 @ 4, 88 @ 5** over
every circuit above, and **97 @ 3, 92 @ 4, 89 @ 5, 88 @ 6** over those with no
imported material anywhere in their lineage. At unconstrained depth the published
floor is 88 (Jean, ePrint 2026/1481) and stays 88; Sun–Yang–Li's 89 (ePrint
2025/1493) states no depth. The project's earlier circuits (89 @ depth 10, 98 @
depth 3, 91 @ depth 6) remain in the repository for the archival record; each is
dominated by a circuit above.

Four points are worth isolating. First, depth 3 is the known minimum depth for
AES MixColumns (stated e.g. by Shi, Feng, and Xu; an output depending on w
inputs needs depth at least ⌈log₂ w⌉, and MixColumns has outputs of weight 7),
so the contribution of the 97-gate circuit is the count at that depth, not the
depth. Second, the 89-gate depth-5 circuit is shallower than any published
circuit of fewer than 94 gates whose depth is stated; the published sub-89
point (88, Jean) sits at depth 7, so neither dominates the other and both are
on the published frontier. Third, the depth-7 88 was found 2026-07-26 by this
project's own search along its own logged lineage — from-scratch 97 @ depth 3 →
89 @ depth 6 → 89 @ depth 5 → a ρ²-symmetric 94 @ depth 5 → 88 @ depth 7 — with
no imported circuit anywhere in the chain. Fourth, the depth-6 88 (found
2026-07-28) is the first 88 this project reached from scratch, on an independently
rooted lineage (randomized XOR trees over the raw inputs → 89 → 88 @ depth 7 →
88 @ depth 6 by the Pareto depth tie-break, with the cross-pollination routes
audited closed); it is what makes 88 @ depth 6 a frontier improvement rather than
a re-derivation, while the depth-5 88 (found 2026-07-29) — reached through a seed
chain that passes through Jean's published circuit — is reported as derived work
and claims nothing about independence.

Beyond the circuits, the note reports machine-checked *local* certificates for
the 88-gate plateau: 47 canonical 88-gate circuits have exhaustively empty
remove-≤3 shells (so any 87 differs from each of them by ≥ 4 masks — this
project's own 88 @ depth 7 is *not* one of the 47); the 88 @ depth 6 has an
exhaustively empty remove-≤3 shell too (all 1,540 k = 2 and all 27,720 k = 3
windows), so any 87 differs from it by ≥ 4 masks as well, and the 88 @ depth 5
has an empty k = 2 shell (≥ 3 masks) but its k = 3 shell was **never swept**, so
with the 88 @ depth 7 it is one of the two least-certified circuits here;
105,801 of the ≈ 139,878
harvested distinct 88-gate mask sets are proven irreducible at k = 2; ≈ 165
million exact window decisions returned zero reducible windows. Windowed SAT
(UNSAT to k = 16 and k = 15 on two family anchors, 0 SAT anywhere) is evidence,
not proof — it is relative to the encoding's fixed slot order. None of this
bounds 87 away globally.

Each circuit is verified by two shipped software paths: `verify.py` against a
from-scratch GF(2^8) MixColumns, and `audit/cleanroom_verify.py` against a
separately written byte-level reference with deterministic random tests and
adversarial rejection checks. The Verilog testbenches add a simulation path
when Icarus Verilog is available.

## 3. Honest scope

- **Not optimality.** Minimum 2-input-XOR circuit size, the Shortest Linear
  Program problem, is NP-hard; we prove no count here minimal, and the
  neighbourhood certificates above are local. We claim only that these are the
  smallest we have found or seen published, at depths 3, 4, 5 and 6 — not at
  unconstrained depth, where 88 is Jean's count and Jean has priority.
- **Source-checked baselines.** The published depth–count frontier we compare
  against: 99 @ depth 3 (Shi, Feng, and Xu, ToSC 2023); 97 @ depth 4 and 94 @
  depth 5 (Osvik and Canright, ePrint 2024/1076, Appendices G and F); 92 @
  depth 6 (Maximov); and, at unconstrained depth, 89 (Sun–Yang–Li, ePrint
  2025/1493, depth not stated) and 88 @ depth 7 (Jean, ePrint 2026/1481). The
  earlier s-XOR baselines (91: Lin et al., CT-RSA 2021; Yuan et al., ToSC 2024)
  are comparable because a k-instruction s-XOR program translates directly into
  a k-gate 2-input XOR circuit. Other cost models (multi-input XOR gates,
  gate-equivalent area, quantum CNOT) are not comparable and are not claimed
  against; see `PRIOR_ART.md` and its Corrections. Counts and depths are
  invariant under bit relabeling, so no comparison depends on convention. The
  depths quoted for Jean (7) and for Sun–Yang–Li (9) are this project's own
  measurements of its own transcriptions; neither paper states a depth. Both are
  *forced*: the ASAP least-fixpoint schedule over each published mask set — the
  shallowest either admits — still gives 7 and 9, so neither can be rescheduled
  shallower (`PRIOR_ART.md`, frontier-table footnote).
- **Provenance.** 97 @ 3 and 92 @ 4 are from scratch; 89 @ 5 and 88 @ 7 are on
  this project's own lineage, rooted in a from-scratch 97 @ 3; 88 @ 6 is from
  scratch on a second, independently rooted lineage; **88 @ 5 and 88 @ 8 are
  derived from published work** — both seed chains pass through Jean's 88, which
  is credited wherever those circuits appear. **All four 88s** were found by
  author-directed LLM-agent campaigns, in two chapters: 88 @ 7 and 88 @ 8 by a
  24-agent campaign over 2026-07-26/27, and 88 @ 6 and 88 @ 5 by a later
  multi-day sixteen-process fleet of the same engine, built and operated by the
  same agents, on 2026-07-28 and 2026-07-29. The published method is
  dependency-free Python that reproduces 97 @ 3, 92 @ 4 and 89 @ 5 — plus a
  single-worker re-run of 88 @ 7 — with no AI system in the loop; **88 @ 6 has no
  single-command reproduction**, and its root constructor, seed and full worker
  log are published in its place (see the note's Method section and the method
  repository).
- **One convention.** All counts hold for the single executable convention in
  `verify.py`. A different bit order or a transposed matrix is a different
  problem; re-derive the targets under your convention before comparing.
- **Circuits vs. method.** The artifacts are self-contained and permanently
  verifiable; no claim depends on how they were found. The search method (a
  value-set shortest-linear-program local search with plateau walking and
  destroy-rebuild moves) is
  published with run evidence and reproduction instructions at
  <https://github.com/Joe-b-20/slp-plateau-search>. Reproduction times, measured
  2026-07-27 with the shipped v2 engine and dependency-free Python: the
  from-scratch 97 @ depth 3 in 81 s on one core; the 89 @ depth 5 in 19 s and
  22 s from shipped seeds, against 592 s for the archived 2026-07-14 run on the
  v1 engine; the 88 @ depth 7 in 19.4 and 31.0 minutes in two single-worker
  re-runs from the ρ²-symmetric 94 seed, against 32.9 minutes in the archived
  ten-worker run. These are measurements, not promises, and the re-runs are
  re-runs, not independent confirmations.

## 4. Reproduce

~~~text
python3 verify_all.py
~~~

Runs both shipped software paths; `python3 verify.py` alone is the faster
repository-only check. With Icarus Verilog installed,
`python3 verify_all.py --with-verilog` adds the hardware path (or
`python3 verify_verilog.py` for the testbenches alone). Canonical-hash metadata
is reproduced by
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
