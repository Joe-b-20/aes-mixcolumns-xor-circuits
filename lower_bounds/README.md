# Lower bounds for the XOR-gate count of AES MixColumns

This folder holds a computer-assisted proof that every circuit of two-input XOR gates computing one
column of AES MixColumns has at least **75** gates, and a description of a certified extension to **76**.
With the verified 88-gate circuits of this repository:

    75 <= L(M) <= 88        the claim of this folder: proof note (review draft, version 1.1, 2026-10-02)

A certified extension to 76 exists but is not published and not claimed here; `bound_76/README.md` states the
facts about it. Nothing here says that 88 is optimal or gives an 87-gate circuit.

## Status, stated plainly

| | the 75 bound | the 76 extension |
|---|---|---|
| what it is | one self-contained proof note (`PROOF_NOTE_75.md` / `.pdf`, 18 pages) with every lemma proved in the text, fourteen finite facts computed by programs, and exact certificates for the last two steps | a 2,200-line internal proof document that extends the 75 argument by about twenty further families of inequalities, with exact certificates for every case; described in `bound_76/README.md`, not yet published |
| how it was produced | with large-language-model assistance under the author's direction; certificates found by an LP solver | the same way, in a two-day campaign (2026-09-29/30) |
| how it has been checked | by programs (this folder) and by independent machine reviews: three adversarial reviews on 2026-09-23 and a from-scratch recomputation plus a further adversarial review on 2026-10-01 (`PROOF_NOTE_75.md`, section 13) | by programs (three independent certificate routes, standard-library checkers) and by machine referee passes over the new inequalities; its document states the theorem conditionally on the checkers' acceptance |
| human review | none yet | none yet |
| formalized in a proof assistant | no | no |
| verification material here | complete (`checks/`, about 2 minutes) | none yet: a factual description only; the document, the certificates (about 180 MB) and the full package (948 MB) are kept by the author until the document is rewritten as a standalone note |

The honest one-line summary: 75 is proved to the standard of "a written argument plus machine-checked
finite facts and certificates, reviewed several times by independent programs and machine reviews, by no human
yet"; 76 is proved to the standard of "machine-checked certificates plus a long internal written argument,
reviewed once by machine, not yet published".

## Read

- `PROOF_NOTE_75.md` (also `PROOF_NOTE_75.pdf`, version 1.1): the theorem, the circuit model, the argument (sections 1-11),
  the finite facts (12), what the programs check versus what the argument must establish (12), the review
  record (13), and the commands (14).
- `bound_76/README.md`: the facts about the 76 extension and its status.

## Verify (Python 3, standard library)

    sh lower_bounds/checks/run_all.sh              # about 2 minutes; stops at the first failure, ends with ALL CHECKS PASSED
    sh lower_bounds/checks/run_all.sh --with-lp    # also the optional LP cross-check (needs numpy and scipy)

The runner exits nonzero if any script fails or if the stress report lists a failure or no circuits (version
1.0's runner piped each script into `tail` and could not report a failure; fixed 2026-10-02 after an external
review). Script by script (expected outputs in `checks/EXPECTED_RESULTS.md`; every script exits nonzero on failure):

| script | what it establishes | runtime |
|---|---|---|
| `finite_facts.py` | every finite fact F1-F14 of the note, from the GF(2^8) definition of MixColumns; ends with `ALL FINITE PREMISES RECOMPUTED AND MATCH` | 35 s |
| `check72.py`, `check73.py` | the finite enumerations of Propositions 8.4 and 9.2 and rho_6(M^T) = 28 | 1 s |
| `check_dark_source.py` | the weight <= 12 zero-sum subsets behind fact F13 (84, 276, 1300, 8112; rho_10 = 29; 736 words) | 10 s |
| `certify74.py`, `independent74.py` | G = 73: 262 profiles, 524 oriented claims, 484 exact certificates, complete coverage (two independent implementations) | 5 s |
| `certify75.py`, `independent75.py` | G = 74: 1,102 profiles, 2,204 oriented claims, 4,057 exact certificates, 9,604 references, 927 direct exclusions, largest weighted right-hand side -1 (two independent implementations) | 30 s |
| `stress.py` | cross-check: every identity and every inequality row of the note on the circuits of this repository and their canonical transposes (0 failures); `stress.py <corpus> [limit]` runs a corpus file too | 2 s |
| `lp_regen.py` | optional (numpy, scipy; `--with-lp`): an LP model written from the note regenerates all 2,204 oriented claims at G = 74 with the same bounds | 20 s |

What the programs cannot check: that the inequalities are necessary conditions for circuits, that the
two-step potential argument is sound, and that the steady tail exists. That is sections 1-11 of the note,
and it is what a reviewer must read.

## Provenance of the files

- `checks/certify74.py`, `CERTIFICATES74.json`, `independent74.py`, `certify75.py`, `CERTIFICATES75.json`,
  `independent75.py`, `check72.py`, `check73.py`, `check_dark_source.py`, `short_code.json`: byte-identical
  copies from the method repository's 75 bundle (`slp-plateau-search`, folder `75/research_deep/` and
  `75/research_push/global/`), except that three scripts have one path line changed for this flat layout
  (marked with a comment).
- `checks/finite_facts.py`, `stress.py`, `lp_regen.py`: written on 2026-10-01 from the proof text, as an
  independent recomputation.
- `PROOF_NOTE_75.md`: consolidates the bundle's documents PROOF.md (sections 1-2), PROOF67, PROOF69,
  WEIGHTED_ADJOINT, PROOF70, DOUBLE_TRANSPOSE, PROOF72, PROOF73, PROOF74, PROOF75 and their lemma files into
  one argument. Nothing in the argument is new relative to the bundle; the consolidation is the author's.

## Cite

This folder was first published as release v4.0.0 of the repository (2026-10-01, commit `4e12c2a`), archived on
Zenodo as version DOI [10.5281/zenodo.23091495](https://doi.org/10.5281/zenodo.23091495). Cite that version DOI for
the review draft; the concept DOI 10.5281/zenodo.21299092 always resolves to the latest release.

## Versions

| version | date | content |
|---|---|---|
| 1.0 | 2026-10-01 | first review draft of the 75 note; 76 described (release v4.0.0, DOI 10.5281/zenodo.23091495) |
| 1.1 | 2026-10-02 | after an external review: the runner now fails loudly (no pipe into `tail`; stress and LP scripts exit nonzero; LP cross-check optional), one cross-reference in the note fixed (Lemma 10.2 / F9), the 76 no longer displayed as a bracket here, CI runs the package |
