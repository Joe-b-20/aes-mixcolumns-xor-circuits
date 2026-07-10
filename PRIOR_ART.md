# Prior-art audit for the comparison claims

This file lets a skeptical reader audit every comparison made in this
repository without re-deriving the literature. It states, for each baseline:
the exact source, the exact reported figure, the cost model, and why it is or
is not comparable.

**Literature-search cutoff: 2026-07-10.** If you know of a published
implementation of AES MixColumns with fewer than 91 two-input XOR gates (or
fewer than 99 at depth 3) that predates this repository, please open an issue.

## The cost model, and which published numbers are comparable

Our model (defined executably in `verify.py`): a circuit is an ordered list of
free-standing 2-input XOR gates over GF(2); cost is the number of gates; depth
is the longest input-to-output gate path. The literature sometimes calls this
model **g-XOR** or an **SLP** (straight-line program) implementation.

**The s-XOR (in-place) model is comparable.** An s-XOR program is a sequence
of in-place instructions `x[i] <- x[i] XOR x[j]` on 32 registers initialized
with the inputs, such that at the end every output resides in a register.

> **Proposition.** Every s-XOR program with `k` instructions yields a circuit
> of exactly `k` free-standing 2-input XOR gates computing the same map, with
> the same depth or less.
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

## Claim 1: 89 gates improves on the smallest published count (91)

| Source | Reported figure | Model | Where stated |
|---|---|---|---|
| Lin, Xiang, Zeng, Zhang, *A Framework to Optimize Implementations of Matrices*, CT-RSA 2021, LNCS 12704. DOI: [10.1007/978-3-030-75539-3_25](https://doi.org/10.1007/978-3-030-75539-3_25) | **91 XORs** — "we find an implementation of AES MixColumns using only 91 Xors, which is currently the shortest implementation to the best of our knowledge" | s-XOR (comparable by the Proposition) | Abstract; result tables in the paper |
| Maximov, *AES MixColumn with 92 XOR gates*, IACR ePrint [2019/833](https://eprint.iacr.org/2019/833) | **92 XOR gates, depth 6** — "a short linear program for AES MixColumn with 92 XOR gates and depth 6" | g-XOR (this model) | Abstract; full listing in the note |
| Xiang, Zeng, Lin, Bao, Zhang, ToSC 2020(2). DOI: [10.13154/tosc.v2020.i2.120-145](https://doi.org/10.13154/tosc.v2020.i2.120-145) | 92 s-XOR | s-XOR | Paper (ties Maximov's count) |
| Yuan, Wu, Shi, Zhang, Zhang, ToSC 2024(2). DOI: [10.46586/tosc.v2024.i2.322-347](https://doi.org/10.46586/tosc.v2024.i2.322-347) | 91 XOR (s-XOR metric; in-place quantum framing, depth 13) | s-XOR | Abstract ("two implementations with 91 XOR counts") |
| Kranz, Leander, Stoffelen, Wiemer, ToSC 2017(4) | 97 XOR | g-XOR | Historical progression point |

Independent tabulations agreeing that 91 is the published minimum as of the
cutoff:

- Shi, Feng, Xu, ToSC 2023(4), Table 3 ("XOR/depth costs of AES MixColumns"):
  minimum listed entry is **91 / depth 7 [LXZZ21]**; also lists 92/6 [Max19],
  92/6 [XZL+20], 94/6 [TP20].
- Pehlivanoğlu, Demir, PeerJ Computer Science 2024
  (DOI: [10.7717/peerj-cs.1820](https://doi.org/10.7717/peerj-cs.1820)),
  Table 5: 2-input-XOR-only rows are 95, 94, 92, 92, **91** (Lin et al.).
- Xu, Sun, ToSC 2026(2) (also arXiv:2511.18226), Table 4: AES row lists
  **91\*** (LXZZ21 and YWS+24, starred as state of the art), 92, and their own
  classical result 105.
- NIST CSRC Circuit Complexity project,
  [List of circuits](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits)
  (checked 2026-07-10): the AES MixColumns entry (shared with Square and Mugi)
  is Maximov's circuit, file `Square-AES-Mugi--XOR=92--maximov.circ.txt`
  (92 XOR, depth 6).

**Conclusion:** the smallest published comparable count as of the cutoff is
**91**; the 89-gate circuit in `circuits/mixcolumns_89gates.json` uses two
fewer. We do not claim optimality.

## Claim 2: 98 gates at depth 3 improves on the published depth-3 record (99)

Depth-3 lineage in the 2-input XOR model, as documented by Shi, Feng, and Xu
(ToSC 2023(4), pp. 489–510, DOI:
[10.46586/tosc.v2023.i4.489-510](https://doi.org/10.46586/tosc.v2023.i4.489-510)):

| Year | Count @ depth 3 | Source (as cited in SFX23) |
|---|---|---|
| 2019 | 105 | [LSL+19] |
| 2021–2022 | 103 | [BFI21]; Liu et al., ToSC 2022(1) [LWF+22] |
| 2023 | 102 | [LZW23] |
| 2023 | **99** | Shi, Feng, Xu — "we find an implementation of AES MixColumns of depth 3 with 99 XOR gates, which represents a substantial reduction of 3 XOR gates compared to the existing record of 102 XOR gates" |

No later comparable-model depth-3 result below 99 was found as of the cutoff
(the only later depth-3 work found, HILL in ToSC 2026(1), reports GE-area
figures in a mixed 2/3-input model — see below).

Depth 3 is the known minimum depth for this map (stated e.g. in SFX23: an
output depending on `w` inputs needs depth at least `ceil(log2 w)`, and
MixColumns has outputs of weight 7), so the depth cannot be reduced further;
only the count at depth 3 can.

**Conclusion:** the published depth-3 record is 99; the 98-gate circuit in
`circuits/mixcolumns_98gates_depth3.json` uses one fewer at the same
(minimum) depth.

## Claim 3: 91 gates at depth 6 matches the smallest published count at lower depth

- Smallest published count: 91 (Lin et al., see Claim 1), listed at **depth 7**
  in both SFX23 Table 3 and PeerJ CS 2024 Table 5 (secondary tabulations of
  the primary result); Yuan et al.'s 91 is at in-place depth 13.
- Smallest published count **at depth 6**: 92 (Maximov, ePrint 2019/833; also
  92/6 [XZL+20] and 94/6 [TP20] per SFX23 Table 3).

**Conclusion:** the 91-gate depth-6 circuit in
`circuits/mixcolumns_91gates_depth6.json` ties the smallest published count
while using one gate fewer than any published depth-6 circuit.

## Non-comparable results

These published figures are sometimes quoted next to XOR counts but use
different cost functions; none of them is claimed against, in either
direction:

- **44 gates at depth 3** (Pehlivanoğlu–Demir, PeerJ CS 2024): composed of
  5 XOR2 + 7 XOR3 + 32 XOR4 gates — a multi-input gate model.
- **270.4 GE at depth 3** (HILL: Li, Wei, Li, Guo, ToSC 2026(1), DOI:
  [10.46586/tosc.v2026.i1](https://tosc.iacr.org/index.php/ToSC/article/view/12794)):
  gate-equivalent area under a weighted mixed 2/3-input "h-XOR" metric.
- **105–107 CNOTs at depth 10** (Zhang et al., IEEE TC 2024 — 105, the
  record; Shi–Feng, ASIACRYPT 2024, ePrint
  [2024/381](https://eprint.iacr.org/2024/381) — 107; Xu–Sun, ToSC 2026(2) —
  105–107): in-place quantum CNOT circuits, a different resource model (and
  numerically above 91 in any case).

## How this audit was compiled

Two multi-source literature sweeps (2026-07-10) over IACR ePrint, ToSC/FSE,
CHES/TCHES, CT-RSA, Springer, arXiv, PeerJ, and the NIST Circuit Complexity
list, cross-checking every comparison table found against the primary papers.
Negative claims ("nothing below 91") rest on those tables and targeted
searches, not exhaustive enumeration; the strongest independent corroboration
is that every 2024–2026 paper checked — each with a direct incentive to cite
any smaller result — bottoms out at 91.
