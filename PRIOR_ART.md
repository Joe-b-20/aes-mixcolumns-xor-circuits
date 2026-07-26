# Prior-art audit for the comparison claims

This file lets a skeptical reader audit every comparison made in this
repository without re-deriving the literature. It states, for each baseline:
the exact source, the exact reported figure, the cost model, and why it is or
is not comparable. (For the provenance of *our* circuits — the search method,
the untouched run archives, and per-record reproduction — see the companion
repository [`slp-plateau-search`](https://github.com/Joe-b-20/slp-plateau-search).)

**Literature-search cutoff: 2026-07-23** (see Corrections below for what the
earlier 2026-07-10/15 sweeps got wrong). If you know of a published
implementation of AES MixColumns in a comparable model that beats a point
claimed here — fewer than 97 at depth 3, 92 at depth 4, or 89 at depth 5 —
please open an issue.

## Corrections

- **2026-07-23.** Two publications change the comparison landscape, one of
  which our earlier sweeps missed:
  - Sun, Yang, Li, *Revisit the Boyar-Peralta Algorithm to Solve the Shortest
    Linear Program Problem*, ePrint [2025/1493](https://eprint.iacr.org/2025/1493)
    (posted 2025-08-19), reports **89 g-XOR** for AES MixColumns (depth not
    stated). This predates this repository. Our sweeps of 2026-07-10/15 —
    and the 2026 comparison tables we corroborated against (HILL Table 13;
    Xu–Sun ToSC 2026(2) Table 4, which still lists 91 as state of the art) —
    missed it. Statements previously made here that "the smallest published
    count is 91" were therefore wrong, and the earlier claim that our
    89-gate circuits were "two fewer than the smallest published count" is
    withdrawn.
  - Jean, *88-XOR Implementation of the AES MixColumns Matrix*, ePrint
    [2026/1481](https://eprint.iacr.org/2026/1481) (posted 2026-07, after
    this repository's releases), gives an **88-XOR, depth-7** circuit
    (count and depth independently re-verified by us from its listing). The
    published count floor is now 88.
  - What stands unchanged: the depth-3, depth-4, and depth-5 points claimed
    here (97, 92, 89) remain the smallest we are aware of at their depths,
    and all three remain on the published depth–count Pareto frontier
    (88 @ depth 7 does not dominate 89 @ depth 5).

## The cost model, and which published numbers are comparable

Our model (defined executably in `verify.py`): a circuit is an ordered list of
free-standing 2-input XOR gates over GF(2); cost is the number of gates; depth
is the longest input-to-output gate path. The literature sometimes calls this
model **g-XOR** or an **SLP** (straight-line program) implementation.

**The s-XOR (in-place) model is comparable.** An s-XOR program is a sequence
of in-place instructions `x[i] <- x[i] XOR x[j]` on 32 registers initialized
with the inputs, such that at the end every output resides in a register.

> **Proposition.** Every s-XOR program with `k` instructions yields a circuit
> of exactly `k` free-standing 2-input XOR gates computing the same map.
>
> *Proof sketch (SSA unrolling).* Maintain a map `cur` from register index to
> signal name, initialized `cur[i] = input_i`. For each instruction
> `x[i] <- x[i] XOR x[j]`, emit one gate `s_new = cur[i] XOR cur[j]` and set
> `cur[i] = s_new`. Each instruction emits exactly one gate whose parents
> already exist, and after the last instruction `cur` names the outputs. ∎
>
> The converse does not hold (s-XOR is the more restrictive model), so an
> s-XOR count is an upper bound that any g-XOR comparison must respect: a
> published `k`-instruction s-XOR program means a `k`-gate 2-input XOR circuit
> is published.

**Not comparable** (different cost functions; listed in
[Non-comparable results](#non-comparable-results) below): multi-input XOR
gates (XOR3/XOR4), technology-mapped gate-equivalent (GE) area, and in-place
quantum CNOT circuits.

Gate counts and depths in either comparable model are invariant under
input/output bit relabeling, so convention differences (bit order, byte order)
do not affect any comparison below.

## The published depth–count frontier

Every published (depth, count) point we found for AES MixColumns in the
comparable models, with the Pareto frontier in bold:

| Depth | Count | Source | Model |
|---|---|---|---|
| 3 | 105 | [LSL+19], as tabulated in SFX23 Table 3 | 2-input XOR |
| 3 | 103 | [BFI21]; Liu et al., ToSC 2022(1) [LWF+22] | 2-input XOR |
| 3 | 102 | [LZW23] (ePrint 2023/174) | 2-input XOR |
| 3 | **99** | Shi, Feng, Xu, ToSC 2023(4). DOI: [10.46586/tosc.v2023.i4.489-510](https://doi.org/10.46586/tosc.v2023.i4.489-510) | 2-input XOR |
| 4 | **97** | Osvik, Canright, ePrint [2024/1076](https://eprint.iacr.org/2024/1076), Appendix G | 2-input XOR |
| 5 | **94** | Osvik, Canright, ePrint [2024/1076](https://eprint.iacr.org/2024/1076), Appendix F | 2-input XOR |
| 6 | 94 | [TP20], as tabulated in SFX23 Table 3 | 2-input XOR |
| 6 | **92** | Maximov, ePrint [2019/833](https://eprint.iacr.org/2019/833); also Xiang, Zeng, Lin, Bao, Zhang, ToSC 2020(2). DOI: [10.13154/tosc.v2020.i2.120-145](https://doi.org/10.13154/tosc.v2020.i2.120-145) | 2-input XOR / s-XOR |
| 7 | 91 | Lin, Xiang, Zeng, Zhang, CT-RSA 2021, LNCS 12704. DOI: [10.1007/978-3-030-75539-3_25](https://doi.org/10.1007/978-3-030-75539-3_25); tied by Yuan et al., ToSC 2024(2). DOI: [10.46586/tosc.v2024.i2.322-347](https://doi.org/10.46586/tosc.v2024.i2.322-347) | s-XOR |
| n/s | 89 | Sun, Yang, Li, ePrint [2025/1493](https://eprint.iacr.org/2025/1493) (depth not stated) | g-XOR |
| 7 | **88** | Jean, ePrint [2026/1481](https://eprint.iacr.org/2026/1481) (posted after this repository's releases; count and depth re-verified by us) | 2-input XOR |
| 8 | 97 | [KLSW17] (Kranz, Leander, Stoffelen, Wiemer, ToSC 2017(4)) | see note |

Published frontier: **(3, 99), (4, 97), (5, 94), (6, 92), (7, 88)** — with
Sun–Yang–Li's 89 at unstated depth alongside. The circuits in this
repository — 97 @ 3, 92 @ 4, 89 @ 5 — improve the frontier's first three
points by 2, 5, and 5 gates respectively, and all three remain on the
frontier: 88 @ depth 7 has fewer gates but strictly greater depth than
89 @ depth 5, so neither dominates the other. Note: Lin et al.'s 91 (and
depending on reading, KLSW17's 97) are stated in the s-XOR model; the
depth-3 lineage, Osvik–Canright, and Jean are free straight-line 2-input XOR
programs with full listings in the papers.

## Claim 1: 97 gates at depth 3 improves the published depth-3 record (99)

Depth-3 lineage in the 2-input XOR model, as documented by Shi, Feng, and Xu
(ToSC 2023(4), pp. 489–510): 105 [LSL+19] → 103 [BFI21], [LWF+22] → 102
[LZW23] → **99** [SFX23] ("we find an implementation of AES MixColumns of
depth 3 with 99 XOR gates, which represents a substantial reduction of 3 XOR
gates compared to the existing record of 102 XOR gates"). No later
comparable-model depth-3 result below 99 was found as of the cutoff; the only
later depth-3 works found (HILL, ToSC 2026(1); Pehlivanoğlu–Demir, PeerJ CS
2024) use mixed multi-input gate models — see below.

Depth 3 is the known minimum depth for this map (stated e.g. in SFX23: an
output depending on `w` inputs needs depth at least `ceil(log2 w)`, and
MixColumns has outputs of weight 7), so the depth cannot be reduced further;
only the count at depth 3 can.

**Conclusion:** the published depth-3 record is 99; the 97-gate circuit in
`circuits/mixcolumns_97gates_depth3.json` uses two fewer at the same
(minimum) depth.

## Claim 2: 92 gates at depth 4 improves the published depth-4 point (97)

The only published depth-4 AES MixColumns circuit in a comparable model we
found is Osvik and Canright's **97 XORs at depth 4** (ePrint 2024/1076,
Appendix G; full straight-line listing in the paper, positioned by the authors
as "slightly larger but less deep (faster) than the 92-XOR depth 6 result of
Maximov"). We verified that no depth-4 point hides in the broader
low-latency literature: SFX23's Table 3 has entries only at depths 3, 6, 7,
and 8 (its depth-4 rows in Table 5 concern a different involutory matrix, not
AES); LZW23's full body contains no depth-4 AES entry; LWF+22 reports only
103 @ depth 3 for AES.

**Conclusion:** the 92-gate circuit in
`circuits/mixcolumns_92gates_depth4.json` uses five fewer gates than the
published depth-4 point.

## Claim 3: 89 gates at depth 5 — smallest we are aware of at depth ≤ 5

- The only published depth-5 point in a comparable model: **94 XORs at depth
  5** (Osvik and Canright, ePrint 2024/1076, Appendix F). Nothing published
  below 94 gates has depth 5 or less.
- Published counts below 89 exist only at greater depth or unstated depth:
  Jean's 88 is at depth 7 (ePrint 2026/1481, posted after this repository's
  releases; re-verified by us), and Sun–Yang–Li's 89 (ePrint 2025/1493) does
  not state a depth. Lin et al.'s 91 (CT-RSA 2021, s-XOR, depth 7 per SFX23
  Table 3) and Yuan et al.'s 91 (s-XOR) are above 89. See the Corrections
  section for the history of this comparison.
- The NIST CSRC Circuit Complexity project's
  [List of circuits](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits)
  (checked 2026-07-10) lists Maximov's 92 XOR / depth 6 as its AES MixColumns
  entry.

**Conclusion:** the 89-gate circuit in
`circuits/mixcolumns_89gates_depth5.json` uses five fewer gates than the
published depth-5 point, and it remains on the published depth–count Pareto
frontier (88 @ depth 7 does not dominate it). We do not claim the smallest
count at unconstrained depth.

## Earlier claims from this project (v1, superseded)

The repository's original three circuits (89 @ depth 10, 98 @ depth 3, 91 @
depth 6) were records against the then-published frontier when released
(2026-07-10) and remain in `circuits/` for the archival record; each is now
dominated by one of the circuits above. Their original claim statements are
preserved in `bounds.json`.

## Non-comparable results

These published figures are sometimes quoted next to XOR counts but use
different cost functions; none of them is claimed against, in either
direction:

- **44 gates at depth 3** (Pehlivanoğlu–Demir, PeerJ CS 2024): composed of
  5 XOR2 + 7 XOR3 + 32 XOR4 gates — a multi-input gate model.
- **79 "XOR operations" at depth 3**
  ([HILL, ToSC 2026(1)](https://tosc.iacr.org/index.php/ToSC/article/view/12794)):
  a mixed XOR2/XOR3 count under the paper's weighted "h-XOR" metric (its
  Table 9 circuit contains 3-input gates); decomposed to 2-input gates it
  exceeds the pure-XOR2 records. The same paper's 270.4 GE figure is
  technology-mapped area.
- **105–107 CNOTs at depth 10** (Zhang et al., IEEE TC 2024 — 105, the
  record; Shi–Feng, ASIACRYPT 2024, ePrint
  [2024/381](https://eprint.iacr.org/2024/381) — 107; Xu–Sun, ToSC 2026(2) —
  105–107): in-place quantum CNOT circuits, a different resource model (and
  numerically above all the counts discussed here in any case). Xu–Sun's
  classical result is 105 XORs, above the records here.

## How this audit was compiled

Three multi-source literature sweeps (2026-07-10 and 2026-07-15) over IACR
ePrint, ToSC/FSE, CHES/TCHES, CT-RSA, Springer, arXiv, PeerJ, and the NIST
Circuit Complexity list, cross-checking every comparison table found against
the primary papers, including full-text sweeps of the papers where a hidden
depth-4/5 point could plausibly live (LZW23, LWF+22, HILL, Xu–Sun,
Osvik–Canright); plus the 2026-07-23 update recorded in the Corrections
section. Negative claims ("nothing below X") rest on tables and targeted
searches, not exhaustive enumeration — and the July sweeps are themselves a
demonstrated failure mode: they corroborated a 91-XOR floor against every
2024–2026 comparison table, yet ePrint 2025/1493 (89 g-XOR, posted 2025-08)
was missed by those tables and by us alike. Treat every negative claim here
as best-effort with a date, not as proof of absence.
