# Small 2-input XOR circuits for AES MixColumns

*A short note accompanying the verified circuit artifacts in this repository.
The typeset note, `paper/mixcolumns_note.pdf` (LaTeX source in `paper/`), is
the authoritative version; this file is a condensed markdown companion.*

## Abstract

We report **thirteen** explicit implementations of the AES MixColumns linear
transformation as circuits of 2-input XOR gates over GF(2) — the nine
discussed in the results table of Section 2, three earlier circuits kept for
the archival record, and one cancellation-free circuit that answers a
different question (Section 2, "The cancellation-free record"). Four improve the
published depth–count Pareto frontier at their depth, on lineages that contain
no imported circuit: (i) a **97-gate** circuit at depth **3**, the known minimum
depth, improving the 99-gate record of Shi, Feng, and Xu (ToSC 2023); (ii) a
**91-gate** circuit at depth **4**, six gates below the 97-gate depth-4 point
of Osvik and Canright (ePrint 2024/1076); (iii) an **88-gate** circuit at depth **5**,
found from scratch, six gates below Osvik and Canright's 94-gate depth-5 point
and two levels shallower than the published 88 at the same count; and (iv) an
**88-gate** circuit at depth **6**, four gates below the published depth-6 point
(92, Maximov). Those 88s are **not a new gate count**: 88 is the published
floor, held by Jean (ePrint 2026/1481, posted 2026-07-23), **who has priority**.
What they improve is the depth at that count. A further circuit, 88 gates at
depth **7**, **ties** that floor with an independent circuit sharing 61 of 88
internal masks; it does not beat it. Two more 88s, at depths **5** and **8**,
are **derived from Jean's circuit** and reported as derived work. An 89 at depth
5, five gates below the published depth-5 point, is now dominated at its depth
and kept for the record. **Verified frontier: 97 @ 3, 91 @ 4, 88 @ 5 — one line,
entirely this project's own lineage, with no imported material.** Until
2026-07-30 there were two frontiers, the depth-5 point being reachable only
through derived work; the from-scratch circuit **removes this project's
dependence on Jean's circuit at that point, and does not beat it**. No 87 was
found: 47 canonical 88-gate circuits have exhaustively empty remove-≤3
neighbourhoods, as do both from-scratch 88s here. All circuits are
machine-checkable artifacts with a pure-Python verifier that rebuilds the
MixColumns specification from scratch. We make no optimality claim on gate
counts.

## Corrections

Dated entries, in the style of the Corrections section of `PRIOR_ART.md`.

- **2026-09-03 (note version 3.2).** Two corrections, both in Section 2. (i) The
  **corpus-wide deletion negative is now complete**. This note previously
  reported it as decided for the 28,796 mask sets that carry a build order and
  explicitly *undecided* for the other 1,546,720; the whole corpus has since
  been streamed and certified, **88,228,896 of 88,228,896 candidate 87-mask sets
  closed, 0 realisable**, over all 1,575,516 sets. The earlier, weaker statement
  is retained beside the new one as history. (ii) The **census is reconciled**:
  the abstract said "nine explicit implementations" while thirteen circuits
  ship. Thirteen it is — the nine in the results table, three archival circuits,
  and `mixcolumns_102gates_cf`, which had no paragraph anywhere in this note
  despite `README.md` making a cancellation-free claim about it. It has one now,
  with the `L_cf(M) >= 92` certificate that brackets it.
- **2026-08-29 (note version 3.2).** The depth-4 frontier point moves from **92
  to 91**. A 91-gate depth-4 circuit, oracle-verified and on this project's own
  from-scratch cascade lineage, is added in Sections 2 and 3; it improves the
  97-gate published depth-4 point by **six** gates rather than five. Two further
  verified 91s exist in independent lineages and are not shipped. The 92 @ depth
  4 is **retained, not withdrawn** — its claim stands as made, and it is not a
  dead-gate strip of the 91 (all 92 of its gates are live). Every frontier
  statement dated earlier than today therefore reads 92 at depth 4 and is
  correct as history. **90 @ depth 4 is undecided, not refuted**: the exactness
  result behind the 91 is relative to a fixed mask vocabulary, so nothing here
  says "optimal at depth 4". The same entry corrects two figures in Section 2 —
  the k = 2 irreducibility sweep finished, so the count is all 139,878 harvested
  mask sets, not 105,801 of them — and adds the joint-level UNSAT ladder and the
  deletion regularity.
- **2026-07-30 (note version 3.1).** Adds a third from-scratch 88-gate circuit,
  at depth 5, in Sections 2 and 3. Its root is a randomized XOR tree over the 32
  raw inputs and no imported material is anywhere in its chain, so the **two
  frontiers reported on 2026-07-29 collapse into one**: 97 @ 3, 92 @ 4, 88 @ 5.
  **88 is still not a new count** — it is Jean's (ePrint 2026/1481, posted
  2026-07-23), Jean has priority, and what changed is whose lineage reaches the
  (88, 5) point, not the count. Two statements of version 3 are corrected: the
  89 @ depth 5 is no longer the depth-5 point of any frontier reported here, and
  the derived 88 @ depth 5 is no longer the circuit establishing that point.
  Both are retained, unwithdrawn, with their earlier claims intact.
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
| `mixcolumns_91gates_depth4` | 91 | 4 | 97 (Osvik, Canright, ePrint 2024/1076, App. G) | improves it by 6. **Not claimed optimal**: 90 at depth 4 is undecided, not refuted | own, from scratch |
| `mixcolumns_92gates_depth4` | 92 | 4 | 97 (as above) | improves it by 5; **superseded at its depth** within this repository by the 91 above, and retained. Not a dead-gate strip of it — all 92 gates are live | own |
| `mixcolumns_88gates_depth5_fromscratch` | 88 | 5 | 94 (Osvik, Canright, ePrint 2024/1076, App. F) | improves it by 6, and dominates the published 88 — same count, two levels shallower. **Not a new count**: 88 is Jean's, who has priority | own, from scratch |
| `mixcolumns_89gates_depth5` | 89 | 5 | 94 (as above) | improves it by 5; dominated at its depth by the row above | own |
| `mixcolumns_88gates_depth5` | 88 | 5 | 94 (as above) | improves it by 6, but **derived**, and not a new count; superseded at its point by the from-scratch 88 @ 5 | **derived from Jean's 88** |
| `mixcolumns_88gates_depth6` | 88 | 6 | 92 (Maximov, ePrint 2019/833; also Xiang et al., ToSC 2020, s-XOR) | improves it by 4, and dominates the published 88 — same count, one level shallower. **Not a new count**, same reason. Dominated here by the from-scratch 88 @ 5, a different family (Jaccard 0.323) | own, from scratch |
| `mixcolumns_88gates_depth7` | 88 | 7 | 88 (Jean, ePrint 2026/1481) | **ties it, does not beat it** — an independent circuit at the same point (61/88 masks shared, Jaccard 0.530); Jean has priority. Dominated by the two rows above | own |
| `mixcolumns_88gates_depth8` | 88 | 8 | — | **derived from Jean's 88** (its seed chain passes through it); dominated, so not a frontier point | **derived from Jean's 88** |

One frontier follows: **97 @ 3, 91 @ 4, 88 @ 5**, every point of it on this
project's own lineage with no imported material. (Version 3 of this note
reported two, because the depth-5 point was then reached only through derived
work.) At unconstrained depth the published
floor is 88 (Jean, ePrint 2026/1481) and stays 88; Sun–Yang–Li's 89 (ePrint
2025/1493) states no depth. The project's earlier circuits (89 @ depth 10, 98 @
depth 3, 91 @ depth 6) remain in the repository for the archival record; each is
dominated by a circuit above.

**The cancellation-free record.** One further circuit is shipped and is not in
the table above, because it is not competing on the same axis:
`mixcolumns_102gates_cf`, 102 gates at depth 5, **cancellation-free** — every
gate's two operand masks have disjoint support, so no gate ever destroys a bit
an earlier gate produced (κ = 0, verified by replaying the gate list over
input-dependency bitsets). It is the only such circuit in this repository, and
the best cancellation-free circuit known for this map. Its interest is that the
matching lower bound sits *above* the record: `L_cf(M) ≥ 92`, an integer price
certificate checkable in a fraction of a second with the standard library
(`bounds/cf_gte92/` in the method repository), so the honest cancellation-free
bracket is **92 ≤ L_cf(M) ≤ 102**. Equivalently: **every XOR circuit for
MixColumns with at most 91 gates contains a cancelling gate**, and the 88-gate
record is four gates below the cancellation-free floor — the one proved quantity
in this programme that lies above 88. It says nothing about whether 87 exists.
Counting it and the three archival circuits, thirteen circuits ship.

Five points are worth isolating. First, depth 3 is the known minimum depth for
AES MixColumns (stated e.g. by Shi, Feng, and Xu; an output depending on w
inputs needs depth at least ⌈log₂ w⌉, and MixColumns has outputs of weight 7),
so the contribution of the 97-gate circuit is the count at that depth, not the
depth. Second, the 89-gate depth-5 circuit is shallower than any published
circuit of fewer than 94 gates whose depth is stated; the published sub-89
point (88, Jean) sits at depth 7. Third, the depth-7 88 was found 2026-07-26 by
this project's own search along its own logged lineage — from-scratch 97 @ depth
3 → 89 @ depth 6 → 89 @ depth 5 → a ρ²-symmetric 94 @ depth 5 → 88 @ depth 7 —
with no imported circuit anywhere in the chain. Fourth, the depth-6 88 (found
2026-07-28) is the first 88 this project reached from scratch, on an independently
rooted lineage (randomized XOR trees over the raw inputs → 89 → 88 @ depth 7 →
88 @ depth 6 by the Pareto depth tie-break, with the cross-pollination routes
audited closed), while the derived depth-5 88 (found 2026-07-29) — reached
through a seed chain that passes through Jean's published circuit — is reported
as derived work and claims nothing about independence. Fifth, the from-scratch
depth-5 88 (found 2026-07-30) is what collapses the two frontiers into one:
worker `c_naive`, session 5, restart 16, root `constructors.build("naive",
1958)` — a randomized XOR tree over the 32 raw inputs, rebuilt and confirmed at
146 gates and depth 3 — then 88 @ depth 6 at iteration 33,873 → 88 @ depth 5 at
iteration 37,155 six seconds later on the same depth tie-break, both from walk
chunks of an engine with no disk read path. It **removes this project's
dependence on Jean's circuit at the depth-5 point; it does not beat it**, and 88
remains Jean's count. Its depth 5 is forced: the ASAP least-fixpoint schedule
over its own mask set still places 11 of its 32 output bits at depth 5, a third
distinct depth-obstruction pattern (rows 1, 7, 12, 13, 17, 18, 21, 25, 27, 28,
31) alongside the old plateau's rows 3/27 and the depth-6 88's rows 1/11/17/25.
It shares 42 of 88 masks with Jean's circuit, 32 of them the forced output
targets, so 10 of 56 free masks coincide; over all four column rotations its
largest similarity to anything measured is Jaccard 0.386, at ρ³ of Jean's 88.

Beyond the circuits, the note reports machine-checked *local* certificates for
the 88-gate plateau: 47 canonical 88-gate circuits have exhaustively empty
remove-≤3 shells (so any 87 differs from each of them by ≥ 4 masks — this
project's own 88 @ depth 7 is *not* one of the 47); the two from-scratch 88s, at
depths 6 and 5, each have an exhaustively empty remove-≤3 shell of their own (all
1,540 k = 2 and all 27,720 k = 3 windows, both), so any 87 differs from each of
them by ≥ 4 masks as well, and the derived 88 @ depth 5
has an empty k = 2 shell (≥ 3 masks) but its k = 3 shell was **never swept**, so
with the 88 @ depth 7 it is one of the two least-certified circuits here;
all 139,878 harvested distinct 88-gate mask sets
are proven irreducible at k = 2 — 215,412,120 exact window decisions, 1,540
windows each, zero reducible.

Two further certificate classes, both stronger than the shells above.

**The joint-level ladder.** For the merged 16-dimensional block of our standard
decomposition — the block structure shared by every known 88-gate circuit — no
program of 9, 10, 11, 12, 13, or 14 gates exists: all six levels UNSAT, the
14-level decided 2026-09-01 by a complete single-solver run (kissat 4.0.4,
356,322 core-seconds, on a hash-asserted instance). The block therefore costs
exactly 15, merging the two largest levels saves nothing, and **no 87-gate
circuit exists that shares the block structure of every known 88.** The levels
at 9, 10 and 11 were re-proved independently with a second CNF encoding, 528 of
528 cubes UNSAT at each level, zero disagreements, and the encoding's positive
control fired (a satisfiable cube with a checked witness), so the test can
fail. Scope: an 87 that does not split into these blocks is not excluded by
this ladder.

**Two population-scale negatives.** First, the corpus-wide single-gate deletion
certificate, now **complete**: let `M` be any of the **1,575,516** distinct
verified 88-gate mask sets in the corpus — the corpus entire — and `m` any of
its 56 non-target masks; then `M \ {m}` is not realisable as an XOR
straight-line program over the 32 inputs. **88,228,896 of 88,228,896 candidate
87-mask sets closed, machine-checked, 0 realisable** (40.0 % of them passed the
local necessary condition and were then decided the hard way). So **no 87-gate
MixColumns circuit is obtainable from any known 88 by deleting one gate**, and
the statement allows the surviving 87 masks to be rebuilt in any order
whatsoever — it is strictly stronger than the `B = 56` tripwire, which only asks
whether a middle gate has *a consumer* and not whether that consumer has an
alternative derivation. Two byproducts over the same population: no set has a
duplicated mask, and every set has exactly 56 consumed non-output gates. The
certificate, its positive control, its tooling and its interval-coverage proof
are in `corpus/deletion_certificate/` in the method repository.

*Superseded statement, kept as history.* Versions of this note before 2026-09-01
reported this negative as complete only for the 28,796 sets that carry a build
order, with the consumer-less test "undecided for the 1,546,720 mask-only sets".
Those sets were re-streamed from their sources and certified; the covered
population is now 1,575,516 of 1,575,516, and the two set-identity checks
(symmetric difference against the corpus index; interval tiling of
`[0, 1575516)` with no gap and no overlap) are part of the certificate.

Second: for the verified 88 at depth 5, all 35,960 four-output-row
drop sets were refuted at one gate fewer — no four output rows can be
resynthesised from the rest of the circuit even one gate more cheaply. The same
screen ran to completion on the from-scratch 88 at depth 5.

Windowed SAT (UNSAT to k = 16 and k = 15 on two family anchors, 0 SAT anywhere)
is evidence, not proof — it is relative to the encoding's fixed slot order, and
the joint-level ladder above is the stronger and independently cross-checked
object.

**The scope of all of it.** A negative at radius ≤ 4 carries no information
about whether an 87 exists. These are locality theorems — rigidity statements
about small, completely enumerated neighbourhoods — not bounds. By this
instrument an optimal circuit and a four-gates-too-big circuit are
indistinguishable. The honest bracket is 56 ≤ L(M) ≤ 88. This **extends** the
2026-07-30 scope entry already in this repository; it does not replace it.

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
- **Provenance.** 97 @ 3 and 91 @ 4 are from scratch; 89 @ 5 and 88 @ 7 are on
  this project's own lineage, rooted in a from-scratch 97 @ 3; 88 @ 6 and the
  from-scratch 88 @ 5 are from scratch on second and third independently rooted
  lineages; **the derived 88 @ 5 and the 88 @ 8 are
  derived from published work** — both seed chains pass through Jean's 88, which
  is credited wherever those circuits appear. **All five 88s** were found by
  author-directed LLM-agent campaigns, in two chapters: 88 @ 7 and 88 @ 8 by a
  24-agent campaign over 2026-07-26/27, and the three depth-5/6 ones by a later
  multi-day sixteen-process fleet of the same engine, built and operated by the
  same agents, on 2026-07-28, 2026-07-29 and 2026-07-30. The published method is
  dependency-free Python that reproduces 97 @ 3, 92 @ 4 and 89 @ 5 — plus a
  single-worker re-run of 88 @ 7 — with no AI system in the loop; **neither
  from-scratch 88 has a single-command reproduction**, and for each the root
  constructor, seed and full worker log are published in its place (see the
  note's Method section and the method repository).
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

## 3a. The vocabulary in the provenance fields

`bounds.json`'s `provenance` fields, and the lineage sentences in Section 2,
name internal machinery. The detail is deliberate — it is what lets a skeptic
follow a circuit back to the run that produced it — but nothing else in this
repository defines the words, so:

| term | what it means |
|---|---|
| **campaign** | a dated block of search work with a fixed goal and a published run archive. "Campaign 87" is the block whose goal was an 87-gate circuit; "beat88" is the earlier block whose goal was to get below 88 |
| **fleet** | a set of independent search processes ("workers") run concurrently on one machine from one operator's configuration, sharing nothing but their target. "Sixteen-process fleet" means sixteen such workers |
| **worker** | one search process in a fleet. Names like `c_naive`, `o1`, `o_polish`, `w10_sym94`, `d3_orb90a` are just its configuration label, logged so a result can be traced to the exact process that emitted it |
| **session** | one contiguous execution of a worker; a worker restarted after an interruption begins a new session, and its log numbering continues |
| **restart** | within a session, a reset of the local search back to a stored incumbent after a stall. "Restart 71" is the 71st such reset |
| **walk iteration** | one step of the local search's mask-set walk — one accepted or rejected mutation of the current circuit's mask set. It is the finest-grained timestamp in the logs, which is why two circuits found seconds apart differ by a few thousand iterations |
| **hunt87**, **hunt-deeper** | named configurations of a campaign-87 fleet: `hunt87` searched for 87 gates at any depth, `hunt-deeper` searched for smaller circuits at greater depth |
| **orbit** | a search restricted to circuits invariant under a column rotation (ρ or ρ², the AES column shift), so a 32-bit target is worked as a smaller symmetric one |
| **tripwire**, **B = 56** | the cheap deletability screen: `B` is the number of consumed non-output gates, which is `gates - 32` exactly when no gate is dead or duplicated. `B != 56` on an 88 means a gate can be deleted. See `corpus/tripwire_demo/` in the method repository |

Wall-clock times in `provenance` fields are **local time, UTC−04:00**, and
worker run-times `t` are seconds since that worker process started, not since
the campaign began.

## 4. Reproduce

~~~text
python3 verify_all.py
~~~

Runs both shipped software paths; `python3 verify.py` alone is the faster
repository-only check. With Icarus Verilog installed,
`python3 verify_all.py --with-verilog` adds the hardware path (or
`python3 verify_verilog.py` for the testbenches alone). Canonical-hash metadata
is reproduced by
`python3 scripts/reproduce_canonical_hashes.py --check-bounds`. The regression
suite, which is what CI runs, is
`python3 -m unittest discover -s tests` (`python3 -m pytest -q tests/` also
works).

A circuit that is not one of the shipped records — yours, or a paper's — is
checked with `python3 verify.py --adhoc FILE`, which runs the structural,
correctness and declared-metadata checks and skips the `bounds.json` hash match
that by construction applies only to circuits this repository makes claims
about. That is how the two transcribed published circuits in `prior_art/` are
verified.

Every generated data file regenerates from its own generator, byte-identically:
`scripts/build_matrix.py`, `scripts/build_golden_vectors.py`,
`scripts/build_wrong_answers.py`, `scripts/build_metadata.py`,
`scripts/generate_listings.py`, `scripts/generate_verilog.py` and
`scripts/generate_frontier_svg.py` all take `--check`, and the test suite runs
them that way. Nothing in this repository is hand-edited away from its source.

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
