# If you got this instead — the wrong-answer table

You wired one of these circuits into your design, ran a MixColumns column
through it, and the bytes that came back are not the bytes you expected.
Find your output in the table and the diagnosis is on the same row.

Every value below was **computed**, not transcribed. The script that
computed it is `scripts/build_wrong_answers.py`, which generates this
file, implements all seven conventions from GF(2^8), and prints its own
controls; `python3 scripts/build_wrong_answers.py --check` re-runs them
and fails if a single byte here has drifted.

## The reference input

The probe column is `db 13 53 45`, the canonical MixColumns test vector.
Correct output: **`8e 4d a1 bc`**. Two more probe columns are given so you
can confirm a diagnosis rather than accept a single-column coincidence.

## The table

| what you got for `db 13 53 45` | ... and for `d4 bf 5d 30` | ... and for `01 00 00 00` | what that means |
|---|---|---|---|
| `8e 4d a1 bc` | `04 66 81 e5` | `02 01 01 03` | **Correct** — AES MixColumns, coefficients `[02 03 01 01]`, signal index `j = 8*byte + bit` LSB-first |
| `db 13 53 45` | `d4 bf 5d 30` | `01 00 00 00` | Identity — the circuit does nothing |
| `22 46 0d b7` | `01 6f 84 ec` | `02 03 01 01` | **Transpose** — circulant `[02 01 01 03]` instead of `[02 03 01 01]` |
| `22 46 0d b7` | `01 6f 84 ec` | `02 03 01 01` | **Byte order reversed** — you fed the column `s3 s2 s1 s0` |
| `61 ed 86 d4` | `3f c8 b5 44` | `d8 01 01 d9` | **Bit order reversed inside each byte** — MSB-first, `j = 8*byte + (7-bit)` |
| `4a a9 ad 90` | `a0 54 2a d8` | `d8 d9 01 01` | **Both reversed** — full 32-bit index reversal, `j -> 31-j` |
| `32 a4 1d 55` | `26 5c a3 df` | `0e 09 0d 0b` | **InvMixColumns** — circulant `[0e 0b 0d 09]` |

## What each one means

### **Correct** — AES MixColumns, coefficients `[02 03 01 01]`, signal index `j = 8*byte + bit` LSB-first

`db 13 53 45` -> `8e 4d a1 bc`  ·  `d4 bf 5d 30` -> `04 66 81 e5`  ·  `01 00 00 00` -> `02 01 01 03`

Nothing is wrong. This is the target.

### Identity — the circuit does nothing

`db 13 53 45` -> `db 13 53 45`  ·  `d4 bf 5d 30` -> `d4 bf 5d 30`  ·  `01 00 00 00` -> `01 00 00 00`

You loaded the wrong file, or your gate list never reached the outputs. The output is the input, byte for byte.

### **Transpose** — circulant `[02 01 01 03]` instead of `[02 03 01 01]`

`db 13 53 45` -> `22 46 0d b7`  ·  `d4 bf 5d 30` -> `01 6f 84 ec`  ·  `01 00 00 00` -> `02 03 01 01`

You read the MDS matrix by rows where this project reads it by columns (or vice versa). The 03 and the first 01 have swapped places. This is the single most common mismatch, because both readings are called "the MixColumns matrix" in the literature. Fix: `out[col] = 02*in[col] ^ 03*in[col+1] ^ 01*in[col+2] ^ 01*in[col+3]`, indices mod 4. **See "Two names, one map" below**: this gives exactly the same bytes as byte-order reversal, so the fix may instead be your byte indexing.

### **Byte order reversed** — you fed the column `s3 s2 s1 s0`

`db 13 53 45` -> `22 46 0d b7`  ·  `d4 bf 5d 30` -> `01 6f 84 ec`  ·  `01 00 00 00` -> `02 03 01 01`

Your state bytes are indexed the other way round: signal index `j = 8*(3-byte) + bit`. The map itself is right, the wiring is mirrored. **This produces exactly the same bytes as the transpose** — see "Two names, one map" below — so the table cannot tell you which of the two you did; check both.

### **Bit order reversed inside each byte** — MSB-first, `j = 8*byte + (7-bit)`

`db 13 53 45` -> `61 ed 86 d4`  ·  `d4 bf 5d 30` -> `3f c8 b5 44`  ·  `01 00 00 00` -> `d8 01 01 d9`

You are numbering bits big-endian within the byte. This project uses LSB-first: signal `8*byte + b` is the coefficient of x^b, so signal 0 is the LSB of byte 0 and signal 7 is its MSB. Every output byte comes back bit-mirrored.

### **Both reversed** — full 32-bit index reversal, `j -> 31-j`

`db 13 53 45` -> `4a a9 ad 90`  ·  `d4 bf 5d 30` -> `a0 54 2a d8`  ·  `01 00 00 00` -> `d8 d9 01 01`

Byte order AND bit order flipped. Listed separately because it is what you get from a wholesale `int.from_bytes(..., 'big')` plus MSB-first bit extraction, and it collides with neither of the two single flips.

### **InvMixColumns** — circulant `[0e 0b 0d 09]`

`db 13 53 45` -> `32 a4 1d 55`  ·  `d4 bf 5d 30` -> `26 5c a3 df`  ·  `01 00 00 00` -> `0e 09 0d 0b`

You built the decryption direction. These circuits are FORWARD MixColumns only; this repository ships no InvMixColumns circuit, and inverting one of these gate lists is not a gate-for-gate operation.

## Two names, one map

Transposing the matrix and reversing the byte order are **the same
transformation** on a circulant, so no probe column can separate them.
This is not a coincidence of the probes; it is algebra, and it holds on
every input:

    MixColumns has M[c][d] = coef[(d - c) mod 4].
    Its transpose has     M[d][c] = coef[(c - d) mod 4].
    Reversing byte order conjugates M by c -> 3-c, which sends
    (d - c) mod 4  to  (c - d) mod 4  — the same matrix.

So if you see `22 46 0d b7`, check **both**: is your coefficient row
`[02 01 01 03]`, and is your byte 0 the one this project calls byte 3?
Fixing either one alone fixes the output; fixing both puts you back where
you started.

Every other pair of rows in the table is distinguishable on the first
probe alone.

Computed collision check over all 7 variants on `db 13 53 45`: 6 distinct outputs, 1 colliding group(s).

## If your output is on none of these rows

Then it is not a convention mismatch, it is a wiring bug. Run
`python3 verify.py --adhoc <your_file.json>`: it rebuilds MixColumns from
the GF(2^8) field arithmetic and reports, for each of the 32 output bits,
whether your circuit builds it. A convention mismatch usually gets none
or very few of them right; a wiring bug usually gets 25-31 right.
