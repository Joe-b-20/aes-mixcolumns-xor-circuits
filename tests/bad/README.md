# tests/bad — circuits the verifier must reject

A verifier that accepts everything proves nothing. Each file here is the record
88-gate circuit with **exactly one** defect introduced, and
`tests/test_bad_circuits.py` asserts that `verify.py` names that defect. The
tests run in CI, so a verifier that stopped catching one of these would fail
the build rather than quietly pass.

Every file also carries a `note` field saying what is wrong with it. None of
these is a valid MixColumns circuit; do not use them for anything else.

| file | the defect | what would slip through without this test |
|---|---|---|
| `bad_removed_gate.json` | one gate deleted | a circuit that no longer computes the map |
| `bad_modified_parent_pair.json` | gate 0 XORs a signal with itself | a gate computing 0 |
| `bad_permuted_output_bindings.json` | two output bindings swapped | right gates, wrong wiring to the outputs |
| `bad_reversed_output_bindings.json` | output bit order reversed | the classic convention mistake — see `wrong_answers.md` |
| `bad_incorrect_depth_metadata.json` | declared depth ≠ measured depth | a depth claim taken on trust |
| `bad_incorrect_gatecount_metadata.json` | declared gate count ≠ actual | a gate-count claim taken on trust |
| `bad_forward_reference.json` | a gate reads a signal that does not exist | a malformed straight-line program |
| `bad_missing_output_signals.json` | no `outputSignals` field | a file that says nothing about which signal is which output |

**What is deliberately not here.** A circuit with a gate nothing reads is still
a *correct* MixColumns circuit, so `verify.py` accepts it and no mutant here
tests otherwise. That defect is one the record's gate count would be wrong
about, not one its correctness would be — it is caught by `tools/tripwire.py`
in the [methods repository](https://github.com/Joe-b-20/slp-plateau-search),
which reports it in a fraction of a second on any circuit file.

The independent recomputation in `audit/cleanroom_verify.py` runs a further 14
adversarial tests of its own, including four wrong-convention target sets
(transposed matrix, inverse matrix, reversed byte order, reversed bit order).
Those are built in memory; these are on disk so they can be read.
