#!/usr/bin/env python3
"""Generate wrong_answers.md. Every byte in the table is computed here.

The file maps "the bytes you actually got" to "which convention you got wrong".
That only works if the wrong answers are the real outputs of the real wrong
conventions, so all seven variants -- the correct map, identity, the transpose,
byte-reversal, bit-reversal, both reversals, and InvMixColumns -- are
implemented from GF(2^8) in this script and evaluated on three probe columns.

CONTROLS printed on every run:
  * the "correct" row must equal golden_vectors.txt's db 13 53 45 -> 8e 4d a1 bc;
  * [02 01 01 03] must really be the transpose of [02 03 01 01];
  * InvMixColumns(MixColumns(x)) == x on 200 pseudorandom columns;
  * the collision count claimed in the prose is recomputed, not asserted.

    python3 scripts/build_wrong_answers.py            # regenerate
    python3 scripts/build_wrong_answers.py --check     # fail if stale
"""
import random

from _builders import emit, parse_args  # noqa: E402


def xtime(a):
    a <<= 1
    return (a ^ 0x11B) & 0xFF if (a & 0x100) else (a & 0xFF)


def gf(a, b):
    r, t = 0, a
    for i in range(8):
        if (b >> i) & 1:
            r ^= t
        t = xtime(t)
    return r & 0xFF


def circulant(coef):
    """out[col] = XOR_k coef[k] * in[(col+k) % 4]"""
    def f(s):
        return [
            gf(coef[0], s[c]) ^ gf(coef[1], s[(c + 1) % 4]) ^
            gf(coef[2], s[(c + 2) % 4]) ^ gf(coef[3], s[(c + 3) % 4])
            for c in range(4)
        ]
    return f


MC = circulant([0x02, 0x03, 0x01, 0x01])
MC_T = circulant([0x02, 0x01, 0x01, 0x03])
INV = circulant([0x0E, 0x0B, 0x0D, 0x09])


def revbytes(s):
    return list(reversed(s))


def revbits_byte(b):
    return int(format(b, "08b")[::-1], 2)


def revbits(s):
    return [revbits_byte(b) for b in s]


def rev32(s):
    """full 32-bit index reversal j -> 31-j: reverse bytes AND bits."""
    return revbits(revbytes(s))


VARIANTS = [
    ("**Correct** — AES MixColumns, coefficients `[02 03 01 01]`, "
     "signal index `j = 8*byte + bit` LSB-first",
     MC,
     "Nothing is wrong. This is the target."),

    ("Identity — the circuit does nothing",
     lambda s: list(s),
     "You loaded the wrong file, or your gate list never reached the outputs. "
     "The output is the input, byte for byte."),

    ("**Transpose** — circulant `[02 01 01 03]` instead of `[02 03 01 01]`",
     MC_T,
     "You read the MDS matrix by rows where this project reads it by columns "
     "(or vice versa). The 03 and the first 01 have swapped places. This is "
     "the single most common mismatch, because both readings are called "
     "\"the MixColumns matrix\" in the literature. Fix: "
     "`out[col] = 02*in[col] ^ 03*in[col+1] ^ 01*in[col+2] ^ 01*in[col+3]`, "
     "indices mod 4. **See \"Two names, one map\" below**: this gives exactly "
     "the same bytes as byte-order reversal, so the fix may instead be your "
     "byte indexing."),

    ("**Byte order reversed** — you fed the column `s3 s2 s1 s0`",
     lambda s: revbytes(MC(revbytes(s))),
     "Your state bytes are indexed the other way round: signal index "
     "`j = 8*(3-byte) + bit`. The map itself is right, the wiring is "
     "mirrored. **This produces exactly the same bytes as the transpose** — "
     "see \"Two names, one map\" below — so the table cannot tell you which "
     "of the two you did; check both."),

    ("**Bit order reversed inside each byte** — MSB-first, "
     "`j = 8*byte + (7-bit)`",
     lambda s: revbits(MC(revbits(s))),
     "You are numbering bits big-endian within the byte. This project uses "
     "LSB-first: signal `8*byte + b` is the coefficient of x^b, so signal 0 "
     "is the LSB of byte 0 and signal 7 is its MSB. Every output byte comes "
     "back bit-mirrored."),

    ("**Both reversed** — full 32-bit index reversal, `j -> 31-j`",
     lambda s: rev32(MC(rev32(s))),
     "Byte order AND bit order flipped. Listed separately because it is what "
     "you get from a wholesale `int.from_bytes(..., 'big')` plus MSB-first "
     "bit extraction, and it collides with neither of the two single flips."),

    ("**InvMixColumns** — circulant `[0e 0b 0d 09]`",
     INV,
     "You built the decryption direction. These circuits are FORWARD "
     "MixColumns only; this repository ships no InvMixColumns circuit, and "
     "inverting one of these gate lists is not a gate-for-gate operation."),
]

PROBES = [
    ("db 13 53 45", [0xDB, 0x13, 0x53, 0x45]),
    ("d4 bf 5d 30", [0xD4, 0xBF, 0x5D, 0x30]),
    ("01 00 00 00", [0x01, 0x00, 0x00, 0x00]),
]


def hx(s):
    return " ".join("%02x" % b for b in s)


def main() -> int:
    args = parse_args("wrong_answers.md")

    L = []
    A = L.append
    A("# If you got this instead — the wrong-answer table")
    A("")
    A("You wired one of these circuits into your design, ran a MixColumns column")
    A("through it, and the bytes that came back are not the bytes you expected.")
    A("Find your output in the table and the diagnosis is on the same row.")
    A("")
    A("Every value below was **computed**, not transcribed. The script that")
    A("computed it is `scripts/build_wrong_answers.py`, which generates this")
    A("file, implements all seven conventions from GF(2^8), and prints its own")
    A("controls; `python3 scripts/build_wrong_answers.py --check` re-runs them")
    A("and fails if a single byte here has drifted.")
    A("")
    A("## The reference input")
    A("")
    A("The probe column is `db 13 53 45`, the canonical MixColumns test vector.")
    A("Correct output: **`8e 4d a1 bc`**. Two more probe columns are given so you")
    A("can confirm a diagnosis rather than accept a single-column coincidence.")
    A("")
    A("## The table")
    A("")
    A("| what you got for `db 13 53 45` | ... and for `d4 bf 5d 30` | ... and for `01 00 00 00` | what that means |")
    A("|---|---|---|---|")
    rows = []
    for name, f, why in VARIANTS:
        outs = [f(list(p)) for _, p in PROBES]
        rows.append((name, [hx(o) for o in outs], why))
        A("| `%s` | `%s` | `%s` | %s |" % (
            hx(outs[0]), hx(outs[1]), hx(outs[2]), name))
    A("")
    A("## What each one means")
    A("")
    for name, outs, why in rows:
        A("### %s" % name)
        A("")
        A("`db 13 53 45` -> `%s`  ·  `d4 bf 5d 30` -> `%s`  ·  `01 00 00 00` -> `%s`"
          % (outs[0], outs[1], outs[2]))
        A("")
        A(why)
        A("")
    A("## Two names, one map")
    A("")
    A("Transposing the matrix and reversing the byte order are **the same")
    A("transformation** on a circulant, so no probe column can separate them.")
    A("This is not a coincidence of the probes; it is algebra, and it holds on")
    A("every input:")
    A("")
    A("    MixColumns has M[c][d] = coef[(d - c) mod 4].")
    A("    Its transpose has     M[d][c] = coef[(c - d) mod 4].")
    A("    Reversing byte order conjugates M by c -> 3-c, which sends")
    A("    (d - c) mod 4  to  (c - d) mod 4  — the same matrix.")
    A("")
    A("So if you see `22 46 0d b7`, check **both**: is your coefficient row")
    A("`[02 01 01 03]`, and is your byte 0 the one this project calls byte 3?")
    A("Fixing either one alone fixes the output; fixing both puts you back where")
    A("you started.")
    A("")
    A("Every other pair of rows in the table is distinguishable on the first")
    A("probe alone.")
    A("")
    # report which variants collide on probe 0
    first = {}
    for name, outs, _ in rows:
        first.setdefault(outs[0], []).append(name)
    coll = {k: v for k, v in first.items() if len(v) > 1}
    A("Computed collision check over all %d variants on `db 13 53 45`: %d "
      "distinct outputs, %d colliding group(s)." % (len(rows), len(first), len(coll)))
    A("")
    A("## If your output is on none of these rows")
    A("")
    A("Then it is not a convention mismatch, it is a wiring bug. Run")
    A("`python3 verify.py --adhoc <your_file.json>`: it rebuilds MixColumns from")
    A("the GF(2^8) field arithmetic and reports, for each of the 32 output bits,")
    A("whether your circuit builds it. A convention mismatch usually gets none")
    A("or very few of them right; a wiring bug usually gets 25-31 right.")
    A("")

    rc = emit("wrong_answers.md", "\n".join(L).encode("utf-8"), args.check)

    print()
    print("CONTROL: every cell computed, none transcribed")
    print("  %-58s %-12s %-12s %-12s" % ("variant", "db135345", "d4bf5d30", "01000000"))
    for name, outs, _ in rows:
        plain = name.replace("**", "").split(" — ")[0]
        print("  %-58s %-12s %-12s %-12s" % (plain[:58], outs[0], outs[1], outs[2]))
    print()
    correct_ok = rows[0][1][0] == "8e 4d a1 bc"
    print("  correct row matches golden_vectors.txt (8e 4d a1 bc):", correct_ok)
    print("  all 7 variants distinct on probe 1:", len(first) == len(rows))
    print("  collisions:", coll if coll else "none")
    random.seed(0)
    cols = [[random.randrange(256) for _ in range(4)] for _ in range(200)]
    inv_ok = all(INV(MC(s)) == s for s in cols)
    coef = [0x02, 0x03, 0x01, 0x01]
    tr_ok = all(coef[(-k) % 4] == [0x02, 0x01, 0x01, 0x03][k] for k in range(4))
    print("  sanity: [02 01 01 03] is the transpose of [02 03 01 01]:", tr_ok)
    print("  sanity: InvMixColumns(MixColumns(x)) == x on 200 random columns:", inv_ok)
    return 0 if (inv_ok and tr_ok and correct_ok and rc == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
