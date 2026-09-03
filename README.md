# XOR circuits for AES MixColumns

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21299092.svg)](https://doi.org/10.5281/zenodo.21299092)
[![verify](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml/badge.svg)](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml)

Small 2-input-XOR circuits for one column of AES MixColumns (a fixed linear map
of 32 bits to 32 bits; four copies make one round's MixColumns). The circuits
are plain functions — any masking/side-channel analysis is yours. Nothing is
claimed optimal; the best known lower bound is 56 gates, and it is proved
elsewhere, not here — see [What is known about optimality](#what-is-known-about-optimality).

## Verify (Python 3 standard library only, well under a second)

~~~text
git clone https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits
cd aes-mixcolumns-xor-circuits && python3 verify.py
~~~

~~~text
AES MixColumns rebuilt from GF(2^8): weight profile 20x5 + 12x7  [OK]

[ OK ] mixcolumns_102gates_cf: 102 gates, depth 5 — all 32 outputs correct, SHA fields match
[ OK ] mixcolumns_88gates_depth5: 88 gates, depth 5 — all 32 outputs correct, SHA fields match
   ... ten more ...
[ OK ] mixcolumns_98gates_depth3: 98 gates, depth 3 — all 32 outputs correct, SHA fields match

ALL CIRCUITS VERIFIED.
~~~

Thirteen `[ OK ]` lines, one per circuit. The map is linear, so checking the 32
unit inputs is a **proof of correctness, not a sample**. The verifier rebuilds
the target from the FIPS-197 field arithmetic — never from the circuit under
test, never from a bundled matrix — then also recomputes gate count and depth
(depth is measured, not trusted) and checks each circuit's hashes against
`bounds.json`.

The regression suite, which is what CI runs, additionally requires the verifier
to reject the eight deliberately broken circuits in [`tests/bad/`](tests/bad/):

~~~text
python3 -m unittest discover -s tests     # ~90 s; python3 -m pytest -q tests/ also works
~~~

**Dependencies.** `verify.py`, `audit/cleanroom_verify.py`, the tests and every
generator need nothing but the Python 3 standard library. The optional Verilog
path (`verify_verilog.py`) needs Icarus Verilog — `iverilog` and `vvp` — and
skips itself with `--allow-missing-tools`.

**Got a circuit of your own?** `python3 verify.py --adhoc your_file.json` runs
the same structural, correctness and metadata checks on any file, anywhere on
disk. It skips only the `bounds.json` hash check, which by construction applies
to circuits this repository makes claims about.

## Conventions (normative)

- Bit `i` of the 32 = bit `i mod 8` of byte `i div 8`, least-significant bit
  first. Signals 0–31 are inputs; gate `k` = XOR of two earlier signals and
  becomes signal `32+k`. Depth of a signal = longest path from an input.
- The matrix itself, as data: [`matrix.txt`](matrix.txt) (32 rows × 32 bits,
  SHA-256 in [`matrix.sha256`](matrix.sha256)).
- Byte-level test vectors, including the FIPS-197 worked example
  `db 13 53 45 → 8e 4d a1 bc`: [`golden_vectors.txt`](golden_vectors.txt).
- Got a different answer? [`wrong_answers.md`](wrong_answers.md) maps the
  common mistakes (transposed matrix, reversed bit order, …) to the outputs
  they produce, one lookup each.

Those last three files are **generated, not typed**: `scripts/build_matrix.py`,
`scripts/build_golden_vectors.py` and `scripts/build_wrong_answers.py` compute
every byte in them from the specification, print the controls they ran, and with
`--check` fail if the shipped file has drifted. The test suite runs all of them
that way.

## The circuits

![depth–gate-count frontier: this repo's records vs prior published bests](docs/frontier.svg)

| depth | gates | file | prior published best | note |
|---|---|---|---|---|
| 3 | **97** | `circuits/mixcolumns_97gates_depth3.json` | 99 (Shi–Feng–Xu, ToSC 2023) | depth 3 is the minimum possible |
| 4 | **91** | `circuits/mixcolumns_91gates_depth4.json` | 97 (Osvik–Canright, ePrint 2024/1076) | |
| 5 | **88** | `circuits/mixcolumns_88gates_depth5_fromscratch.json` | 94 (Osvik–Canright) | fewest gates known at any depth — **tied**, not beaten: 88 is Jean's count (ePrint 2026/1481), he found it first, and this circuit is two levels shallower at that count. See [credit](#credit-and-independence) |

Which row do I want? Round-based design → the 88 at depth 5. Heavily
pipelined / latency-critical → the 97 at depth 3. Everything else shipped
(further 88s at depths 6–8, superseded and archival circuits, and the best
known cancellation-free circuit at 102) is in
[`circuits_metadata.csv`](circuits_metadata.csv) with per-circuit depth,
per-output depth, fan-out histogram, and SHA-256. A circuit file's contents
never change under a stable name.

No area or latency figures are offered, and none should be inferred from the
gate count. The only physical datum here is fan-out, in the CSV's
`max_fanout_gate` / `fanout_histogram_gates` columns (the 97 peaks at 5).

## File format

One JSON object with exactly eight keys: `"gates": [[a,b], ...]` (gate k =
signal a XOR signal b, both indices < 32+k), `"outputSignals": [...]` naming
which signal carries each output bit, and `id`, `inputCount`, `gateCount`,
`depth`, `model`, `outputConvention`. **That is all a circuit file contains** —
no hashes and no provenance, because its bytes must never change under a stable
name.

Everything *about* a circuit lives in [`bounds.json`](bounds.json), keyed by
`id`: both SHA-256 hashes (of the file bytes, and of the documented canonical
gate encoding), the verification record, the exact claim being made, and the
provenance — including which circuits descend from published work and whose.
`verify.py` reads it, and the hashes are reproducible with
`python3 scripts/reproduce_canonical_hashes.py --check-bounds`.

`listings/` has the same circuits as plain text, one gate per line; `verilog/`
has a netlist + testbench per circuit, each with the bit convention in its
header (`dont_touch` / `keep` the module or synthesis will restructure it — and
note that re-association can invalidate masking arguments; you own that
analysis).

## What else is here

| | |
|---|---|
| [`bounds.json`](bounds.json) | per-circuit hashes, verification record, exact claim, provenance. `verify.py` depends on it |
| [`PAPER.md`](PAPER.md) | the note: results table, honest scope, what the negative results do and do not say. Typeset version in [`paper/`](paper/) |
| [`PRIOR_ART.md`](PRIOR_ART.md) | who published what, with DOIs; the claim-by-claim comparison and a dated Corrections log |
| [`prior_art/`](prior_art/) | **other people's** circuits, transcribed, so the overlap numbers below can be recomputed. Not records here |
| [`circuits_metadata.csv`](circuits_metadata.csv) | 21 computed columns per circuit. `B` and `expected_B` are defined in `scripts/build_metadata.py`; `B` is **not** a bound |
| [`audit/`](audit/) | `cleanroom_verify.py`, a second verifier written against a separate byte-level reference, plus its recomputed metrics |
| `verify_all.py`, `verify_verilog.py` | run every shipped verification path; add the Icarus Verilog simulation path |
| [`scripts/`](scripts/) | the generators for every derived file, all with `--check`, plus `overlap.py` |
| [`tests/`](tests/) | the regression suite, including the eight mutants the verifier must reject |
| [`LICENSE`](LICENSE) | MIT |

## Credit and independence

Jérémy Jean reached 88 gates first and independently (ePrint 2026/1481);
priority is his. This repo's 88 at depth 7 is an independent circuit sharing
61 of its 88 intermediate values with Jean's. Both circuits are here, so you
can measure that yourself:

~~~text
python3 scripts/overlap.py circuits/mixcolumns_88gates_depth7.json \
                           prior_art/jean_88gates_depth7_eprint_2026-1481.json
#   shared      61
#   Jaccard        = 61/115 = 0.530
~~~

61 shared masks only means something with a calibration beside it. Two
*independently published* circuits — Jean's 88 and Sun–Yang–Li's 89 (ePrint
2025/1493), both in `prior_art/` — share **63** masks at Jaccard **0.553**,
slightly more. Overlap of this size is what independent constructions for this
particular map look like; any two circuits for it share the 32 forced output
masks no matter who found them.

~~~text
python3 scripts/overlap.py prior_art/jean_88gates_depth7_eprint_2026-1481.json \
                           prior_art/sunyangli_89gates_eprint_2025-1493.json
~~~

Two of the shipped 88s (`mixcolumns_88gates_depth5` and
`mixcolumns_88gates_depth8`) have seed chains that pass through Jean's circuit
and are **derived work, not independent constructions**. That disclosure, with
the full mask-checked chain link by link, is in each one's `provenance` field in
[`bounds.json`](bounds.json) — not in the circuit files, which carry no
provenance at all.

## What is known about optimality

One line each. None of these bounds is proved in this repository; each is
proved, with a checkable certificate or a documented solver run, in
[slp-plateau-search](https://github.com/Joe-b-20/slp-plateau-search), which is
also where the instruments, the negative results and the open leads live.

- **Any circuit needs ≥ 56 gates.** The only unconditional lower bound known
  for this matrix, by adaptive gate elimination; certificate and checker in
  `bounds/gte56/`. Honest bracket: 56 ≤ L(M) ≤ 88.
- **Any depth-3 circuit needs ≥ 80 gates**, by an exact rational weak-duality
  certificate that checks in under a second, and **≥ 81** by the dual bound of a
  branch-and-cut run on the same model — a solver result, not a certificate, and
  labelled as such. Both in `bounds/depth3_gte81/`.
- **Any circuit where no gate's inputs share a bit needs ≥ 92** (a
  *cancellation-free* circuit), by an integer price certificate; the 102 shipped
  here is the best such circuit known, so 92 ≤ L_cf(M) ≤ 102. In
  `bounds/cf_gte92/`. This is the only proved quantity in the programme that
  lies *above* 88 — equivalently, every circuit for this map with at most 91
  gates contains a cancelling gate.
- **No 87-gate circuit exists that shares the internal block structure of every
  known 88** (a SAT result: six UNSAT levels, the last decided by kissat 4.0.4
  in 356,322 core-seconds on a hash-asserted instance; CNFs, proofs and logs in
  `encodings/`). An 87 that does not split into those blocks is not excluded.
- **No 87 is one gate-deletion away from any known 88.** Over all 1,575,516
  distinct verified 88-gate mask sets in the corpus, all 88,228,896 candidate
  87-mask sets were machine-checked and **none is realisable**, with the
  surviving masks free to be rebuilt in any order. In
  `corpus/deletion_certificate/`.

**Whether 87 exists at all is open.** Every negative above is either a bound
below 88 or a rigidity statement about a completely enumerated neighbourhood; by
those instruments an optimal circuit and a four-gates-too-big circuit look the
same.

Beat a row of the table? Check it first with
`python3 verify.py --adhoc your_file.json`, then open an issue with the file
attached. We verify it, add its `bounds.json` entry — the hashes, the claim, and
your provenance — and you get named credit in the table and the changelog. (The
`--adhoc` run is not the acceptance step: acceptance is the `bounds.json` entry,
and that is a maintainer action.)

## Cite / license

MIT. Cite via <https://doi.org/10.5281/zenodo.21299092> (`CITATION.cff`).
Sole-author work; no employer IP. Report verification failures as issues with
your Python version and the full output; GitHub issues are the contact route,
and the author's address is on the note in `paper/` if you need it.
