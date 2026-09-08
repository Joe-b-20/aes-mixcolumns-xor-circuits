# XOR circuits for AES MixColumns

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21299092.svg)](https://doi.org/10.5281/zenodo.21299092)
[![verify](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml/badge.svg)](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml)

Small 2-input-XOR circuits for one column of AES MixColumns (a fixed linear map
of 32 bits to 32 bits; four copies make one round's MixColumns). The circuits
are plain functions — any masking/side-channel analysis is yours. Nothing is
claimed optimal; the best known lower bound is 56 gates.

## Verify (Python 3 standard library, under a second)

~~~text
git clone https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits
cd aes-mixcolumns-xor-circuits && python3 verify.py
~~~
~~~text
AES MixColumns rebuilt from GF(2^8): weight profile 20x5 + 12x7  [OK]
[ OK ] mixcolumns_102gates_cf: 102 gates, depth 5 — all 32 outputs correct, SHA fields match
   ... twelve more ...
ALL CIRCUITS VERIFIED.
~~~

The map is linear, so checking the 32 unit inputs is a **proof of correctness,
not a sample**. The verifier rebuilds the target from the FIPS-197 field
arithmetic — never from the circuit under test, never from a bundled matrix —
recomputes gate count and depth rather than reading them, and checks each
circuit's hashes against `bounds.json`. CI additionally runs the regression
suite (`python3 -m unittest discover -s tests`, ~90 s), which requires the
verifier to reject the eight broken circuits in [`tests/bad/`](tests/bad/).

Your own circuit: `python3 verify.py --adhoc your_file.json` runs the same
checks on any file (skipping only the `bounds.json` hash lookup). The optional
Verilog path (`verify_verilog.py`) needs Icarus Verilog.

## Conventions (normative)

- Bit `i` of the 32 = bit `i mod 8` of byte `i div 8`, least-significant bit
  first. Signals 0–31 are inputs; gate `k` = XOR of two earlier signals and
  becomes signal `32+k`. Depth of a signal = longest path from an input.
- The **value** of a signal is the set of input bits it XORs together, written
  as a 32-bit vector. A circuit's **value set** is the set of values its gates
  compute: 88 values for an 88-gate circuit, 32 of them the required outputs.
- The matrix itself, as data: [`matrix.txt`](matrix.txt) (32 rows × 32 bits,
  SHA-256 in [`matrix.sha256`](matrix.sha256)).
- Byte-level test vectors, including the FIPS-197 worked example
  `db 13 53 45 → 8e 4d a1 bc`: [`golden_vectors.txt`](golden_vectors.txt).
- Got a different answer? [`wrong_answers.md`](wrong_answers.md) maps the
  common mistakes (transposed matrix, reversed bit order, …) to the outputs
  they produce, one lookup each.

`matrix.txt`, `golden_vectors.txt` and `wrong_answers.md` are generated from
the specification by `scripts/build_*.py` (each has `--check`; the test suite
runs them).

## The circuits

![depth–gate-count frontier: this repo's records vs prior published bests](docs/frontier.svg)

| depth | gates | file | prior published best | note |
|---|---|---|---|---|
| 3 | **97** | `circuits/mixcolumns_97gates_depth3.json` | 99 (Shi–Feng–Xu, ToSC 2023) | depth 3 is the minimum possible |
| 4 | **91** | `circuits/mixcolumns_91gates_depth4.json` | 97 (Osvik–Canright, ePrint 2024/1076) | |
| 5 | **88** | `circuits/mixcolumns_88gates_depth5_fromscratch.json` | 94 (Osvik–Canright) | fewest gates known at any depth — a **tie** with Jean's 88 (ePrint 2026/1481), who found it first; this one is two levels shallower. **Note the `_fromscratch` suffix**: a second 88 at depth 5 also ships, as `circuits/mixcolumns_88gates_depth5.json`, and that one is **derived from Jean's circuit** |

Which row do I want? Round-based design → the 88 at depth 5. Heavily
pipelined or latency-critical → the 97 at depth 3.

Everything else shipped — further 88s at depths 6–8, superseded and archival
circuits, and the best known cancellation-free circuit at 102 — is listed in
[`circuits_metadata.csv`](circuits_metadata.csv): 21 computed columns per
circuit (depth, per-output depth, fan-out histogram, SHA-256), plus a
`provenance_class` column reduced from `bounds.json` so that
`derived-from-published-work` is one sort away.

Fan-out and per-output depth are reported because in a masked or threshold
implementation they, rather than gate count, drive glitch-extended probing
behaviour and the cost of the refresh network: the 97 @ 3 has a maximum fan-out
of 5. No area or latency figures are offered here, and gate count is not a
substitute for either.

A circuit file's contents never change under a stable name. That is why the
derived 88 keeps the plain `_depth5` name it was published under.

## File format

One JSON object: `"gates": [[a,b], ...]` (gate k = signal a XOR signal b, both
indices < 32+k), `"outputSignals": [...]` naming which signal carries each
output bit, plus `id`, `inputCount`, `gateCount`, `depth`, `model`,
`outputConvention`. That is all — no hashes, no provenance, so the bytes never
change.

Everything *about* a circuit lives in [`bounds.json`](bounds.json), keyed by
`id`: both SHA-256 hashes, the verification record, the exact claim, and the
provenance (including which circuits descend from published work).

`listings/` has the same circuits as plain text. `verilog/` has a netlist and a
testbench for each, with the bit convention in the header; mark the module
`dont_touch`/`keep`, or synthesis will restructure it, and re-association can
invalidate masking arguments.

## What else is here

| | |
|---|---|
| [`bounds.json`](bounds.json) | hashes, verification record, exact claim, provenance per circuit |
| [`PAPER.md`](PAPER.md) | the note: results, scope, what the negatives do and do not say (typeset in [`paper/`](paper/)) |
| [`PRIOR_ART.md`](PRIOR_ART.md) | who published what, claim by claim, with a dated corrections log |
| [`prior_art/`](prior_art/) | other people's circuits, transcribed, so a reader can recompute the overlap numbers below |
| [`audit/`](audit/) | a second, independently written verifier and its recomputed metrics |
| [`scripts/`](scripts/) · [`tests/`](tests/) | generators for every derived file (all with `--check`), `overlap.py`; the regression suite |

## Credit and independence

Jérémy Jean reached 88 gates first and independently (ePrint 2026/1481);
priority is his. This repo's 88 at depth 7 is an independent circuit sharing
61 of its 88 intermediate values with Jean's; both circuits are here:

~~~text
python3 scripts/overlap.py circuits/mixcolumns_88gates_depth7.json prior_art/jean_88gates_depth7_eprint_2026-1481.json
#   shared 61   Jaccard 61/115 = 0.530
~~~

For scale: two *independently published* circuits — Jean's 88 and
Sun–Yang–Li's 89 (ePrint 2025/1493, also in `prior_art/`) — share 63. Overlap
of this size is what independent constructions for this map look like.

Exactly two shipped circuits are derived work: `mixcolumns_88gates_depth5.json`
and `mixcolumns_88gates_depth8.json`, whose seed chains pass through Jean's
circuit. Both are disclosed link by link in their `bounds.json` provenance and
carry `derived-from-published-work` in `circuits_metadata.csv`. Neither is the
frontier point above — that is `mixcolumns_88gates_depth5_fromscratch.json`,
whose chain reads no circuit at all.

## What is known about optimality

One line each. The proofs, instruments, negative results and open leads are in
[slp-plateau-search](https://github.com/Joe-b-20/slp-plateau-search):

- Any circuit needs **≥ 56** gates — the best unconditional bound we are aware
  of for this matrix. So `56 ≤ L(M) ≤ 88`.
- Any depth-3 circuit needs **≥ 80** (checkable certificate) and **≥ 81** by a
  time-limited solver bound.
- Any circuit where no gate's inputs share a bit needs **≥ 92**; the 102 here is
  the best such circuit known — so every circuit of ≤ 91 gates contains a
  cancelling gate.
- **Under that project's block decomposition**, no 87-gate circuit shares the
  internal block structure of every known 88 (a SAT result, six UNSAT levels).
  The decomposition is a choice; whether every known 88 respects it was not
  verified, and the decisive level carries no DRAT proof, so it rests on two
  solvers agreeing on one CNF.
- No 87 is one gate-deletion away from any of **1,575,516 distinct verified
  88-gate value sets** — each a set of 88 intermediate values known to be
  realisable, of which 28,796 carry a full build order — with all 88,228,896
  deletions machine-checked.

Whether 87 exists at all is open: every negative above is either a bound below
88 or a statement about a completely enumerated neighbourhood.

To beat a row of the table, check your circuit with `verify.py --adhoc` and
open an issue with the file. We verify it and add its `bounds.json` entry,
which is the acceptance step; the table and the changelog then carry your
name.

## Cite / license

MIT. Cite via <https://doi.org/10.5281/zenodo.21299092> (`CITATION.cff`).
The search behind these circuits was carried out with heavy use of AI agents
directed by the author, and "we" on these pages means that collaboration.
