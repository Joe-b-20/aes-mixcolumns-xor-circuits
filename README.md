# XOR circuits for AES MixColumns

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21299092.svg)](https://doi.org/10.5281/zenodo.21299092)
[![verify](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml/badge.svg)](https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits/actions/workflows/verify.yml)

Small 2-input-XOR circuits for one column of AES MixColumns (a fixed linear map
of 32 bits to 32 bits; four copies make one round's MixColumns). The circuits
are plain functions — any masking/side-channel analysis is yours. Nothing is
claimed optimal; the best known lower bound is 56.

## Verify (60 seconds, no dependencies)

~~~text
git clone https://github.com/Joe-b-20/aes-mixcolumns-xor-circuits
cd aes-mixcolumns-xor-circuits && python3 verify.py
# ... 13 circuits ...
# ALL CIRCUITS VERIFIED.
~~~

The map is linear, so checking the 32 unit inputs is a **proof of correctness,
not a sample**. The verifier rebuilds the target from the FIPS-197 field
arithmetic — never from the circuit under test, never from a bundled matrix —
then also recomputes gate count and depth (depth is measured, not trusted) and
must reject the broken circuits in `tests/bad/`. CI runs all of it.

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

## The circuits

| depth | gates | file | prior published best | note |
|---|---|---|---|---|
| 3 | **97** | `circuits/mixcolumns_97gates_depth3.json` | 99 (Shi–Feng–Xu, ToSC 2023) | depth 3 is the minimum possible |
| 4 | **91** | `circuits/mixcolumns_91gates_depth4.json` | 97 (Osvik–Canright, ePrint 2024/1076) | |
| 5 | **88** | `circuits/mixcolumns_88gates_depth5_fromscratch.json` | 94 (Osvik–Canright) | fewest gates known at any depth |
| — | | | 88 (Jean, ePrint 2026/1481) | Jean found 88 first; see credit below |

Which row do I want? Round-based design → the 88 at depth 5. Heavily
pipelined / latency-critical → the 97 at depth 3. Everything else shipped
(further 88s at depths 6–8, superseded and archival circuits, and the best
known cancellation-free circuit at 102) is in
[`circuits_metadata.csv`](circuits_metadata.csv) with per-circuit depth,
per-output depth, fan-out histogram, and SHA-256. A circuit file's contents
never change under a stable name.

## File format

One JSON object: `"gates": [[a,b], ...]` (gate k = signal a XOR signal b,
both indices < 32+k), `"outputSignals": [...]` naming which signal carries
each output bit, plus hashes and provenance. `listings/` has the same circuits
as plain text, one gate per line; `verilog/` has a netlist + testbench per
circuit (`dont_touch` the module or synthesis will restructure it — and note
that re-association can invalidate masking arguments; you own that analysis).

## Credit and independence

Jérémy Jean reached 88 gates first and independently (ePrint 2026/1481);
priority is his. This repo's 88 at depth 7 is an independent circuit sharing
61 of its 88 intermediate values with Jean's — measured by
[`scripts/overlap.py`](scripts/overlap.py), which you can run yourself. Two
of the shipped 88s are derived from Jean's and labelled so in their files.

## What is known about optimality

One line each; proofs, instruments, negative results, and open leads live in
[slp-plateau-search](https://github.com/Joe-b-20/slp-plateau-search):

- Any circuit needs ≥ 56 gates (the only known lower bound for this matrix).
- Any depth-3 circuit needs ≥ 81 gates.
- Any circuit where no gate's inputs share a bit needs ≥ 92 (the 102 shipped
  here is the best such circuit known).
- No 87-gate circuit exists that shares the internal block structure of every
  known 88 (a SAT result), and none is one gate-deletion away from any of
  1.58 million known 88-gate solutions. Whether 87 exists at all is open.

Beat a row of the table? Your circuit is one `verify.py` run from being
accepted — open an issue with the file; you get named credit in the table and
the changelog.

## Cite / license

MIT. Cite via <https://doi.org/10.5281/zenodo.21299092> (`CITATION.cff`).
Sole-author work; no employer IP. Report verification failures as issues with
your Python version and the full output.
