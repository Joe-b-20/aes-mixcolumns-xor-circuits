# Other people's circuits

**Nothing in this directory is a result of this project.** These two circuits
were published by other authors; they are shipped here, transcribed, only so
that the overlap and independence numbers this repository quotes can be
recomputed by a reader instead of taken on trust.

| file | gates @ depth | author, source |
|---|---|---|
| `jean_88gates_depth7_eprint_2026-1481.json` | 88 @ 7\* | **Jérémy Jean**, ePrint [2026/1481](https://eprint.iacr.org/2026/1481), Algorithm 1, posted 2026-07-23 |
| `sunyangli_89gates_eprint_2025-1493.json` | 89 @ 9\* | **Sun, Yang, Li**, ePrint [2025/1493](https://eprint.iacr.org/2025/1493), Table 4 (89 g-XOR) |

\* Neither paper states a depth. The depths above are what this repository's
verifier *measures* for the transcribed gate lists, and neither can be
rescheduled shallower.

Each file was transcribed from its paper's listing, with the input bit labels
permuted into this repository's convention — the permutation is recorded in the
file's own `input_permutation_paper_to_repo` field, so the transcription is
reversible and auditable against the paper. Gate lists are byte-for-byte as
imported. Jean has **priority on the 88-gate count**; see `PRIOR_ART.md`.

One consequence of "byte-for-byte as imported": each file's `outputConvention`
text refers to `verify_circuit.py`, the *method* repository's oracle
([slp-plateau-search](https://github.com/Joe-b-20/slp-plateau-search)), which
is where these transcriptions were made and first verified. That file is not
shipped here and the sentence is not about this repository; `verify.py
--adhoc` is the equivalent here. The files are left untouched rather than
edited, because an imported artifact that gets tidied is no longer an import.

## They are not records here

- Neither file appears in `bounds.json`, in the README's records table, in
  `circuits_metadata.csv`, in `listings/`, or in `verilog/`.
- `verify.py` and `audit/cleanroom_verify.py` scan `circuits/` only, so the
  default verification run does not touch this directory and makes no claim
  about it.

## Verifying them anyway

```
python3 verify.py --adhoc prior_art/*.json
# [ OK ] jean_88gates_depth7_eprint_2026-1481.json: 88 gates, depth 7 — all 32 outputs correct
# [ OK ] sunyangli_89gates_eprint_2025-1493.json: 89 gates, depth 9 — all 32 outputs correct
```

`--adhoc` runs the structural, correctness and declared-metadata checks and
skips the `bounds.json` hash match, which by design applies only to circuits
this repository makes claims about.

## What they are here for

```
# the tie: this project's 88 @ 7 against Jean's 88 — 61 shared, Jaccard 0.530
python3 scripts/overlap.py circuits/mixcolumns_88gates_depth7.json \
                           prior_art/jean_88gates_depth7_eprint_2026-1481.json

# the calibration: two independently published circuits, Jean vs Sun–Yang–Li
# — 63 shared, Jaccard 0.553, slightly MORE overlap than the pair above
python3 scripts/overlap.py prior_art/jean_88gates_depth7_eprint_2026-1481.json \
                           prior_art/sunyangli_89gates_eprint_2025-1493.json

# the from-scratch 88 @ 5 against Jean's — 42 shared, 32 of them forced outputs
python3 scripts/overlap.py circuits/mixcolumns_88gates_depth5_fromscratch.json \
                           prior_art/jean_88gates_depth7_eprint_2026-1481.json
```

Overlap is not evidence of derivation in either direction: any two circuits for
this map share their 32 forced output masks no matter who found them. The
calibration line is the point of shipping the second file — 61/0.530 only means
something next to 63/0.553.
