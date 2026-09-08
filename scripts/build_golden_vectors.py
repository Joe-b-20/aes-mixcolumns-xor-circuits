#!/usr/bin/env python3
"""Generate golden_vectors.txt, and run its two controls while doing so.

Every byte of every vector is computed here. Nothing is transcribed from a
paper or from another file in this repository.

CONTROL 1 (matrix path): each output is recomputed by multiplying the input
    vector by the 32 rows of matrix.txt.
CONTROL 2 (circuit path): each output is recomputed by replaying a shipped
    88-gate circuit gate by gate over concrete bits -- not values -- and
    reading the signal that carries each output. This is the transcript the
    file's "HOW TO USE THESE" section describes.

Both must agree with verify.py's from-scratch GF(2^8) specification on all
eleven vectors, or this script exits nonzero.

    python3 scripts/build_golden_vectors.py            # regenerate
    python3 scripts/build_golden_vectors.py --check     # fail if stale
"""
import json

from _builders import ROOT, emit, parse_args  # noqa: E402

import verify  # noqa: E402

SPEC = verify.mixcolumns_target_masks()
MATRIX_ROWS = [r for r in (ROOT / "matrix.txt").read_text(encoding="utf-8").split() if r]
CIRCUIT = "circuits/mixcolumns_88gates_depth5_fromscratch.json"

VECTORS = [
    ("the canonical MixColumns test column, quoted everywhere in the "
     "Rijndael/FIPS-197 literature", [0xDB, 0x13, 0x53, 0x45]),
    ("FIPS-197 Appendix B, round 1: the first MixColumns column of the "
     "standard's own worked example", [0xD4, 0xBF, 0x5D, 0x30]),
    ("the second column of that same FIPS-197 Appendix B round-1 state",
     [0xE0, 0xB4, 0x52, 0xAE]),
    ("all-ones: every input bit set (exercises every gate)",
     [0xFF, 0xFF, 0xFF, 0xFF]),
    ("all-zero: a linear map must send 0 to 0", [0x00, 0x00, 0x00, 0x00]),
    ("the constant column 01 01 01 01: a fixed point, because the MDS row "
     "sums to 1 in GF(2^8)", [0x01, 0x01, 0x01, 0x01]),
    ("unit vector: input signal 0 only (byte 0, LSB)", [0x01, 0x00, 0x00, 0x00]),
    ("unit vector: input signal 7 only (byte 0, MSB)", [0x80, 0x00, 0x00, 0x00]),
    ("unit vector: input signal 24 only (byte 3, LSB)", [0x00, 0x00, 0x00, 0x01]),
    ("unit vector: input signal 31 only (byte 3, MSB)", [0x00, 0x00, 0x00, 0x80]),
    ("one whole byte set: byte 1 = ff, the rest zero",
     [0x00, 0xFF, 0x00, 0x00]),
]


def bytes_to_vec(bs):
    """4 bytes -> 32-bit int, index j = 8*byte + bit, LSB-first inside a byte."""
    v = 0
    for i, b in enumerate(bs):
        for k in range(8):
            if (b >> k) & 1:
                v |= 1 << (8 * i + k)
    return v


def vec_to_bytes(v):
    return [(v >> (8 * i)) & 0xFF for i in range(4)]


def idx_list(v):
    return [j for j in range(32) if (v >> j) & 1]


def apply_spec_masks(v):
    o = 0
    for r in range(32):
        if bin(SPEC[r] & v).count("1") & 1:
            o |= 1 << r
    return o


def apply_matrix(v):
    """out bit r = parity of (row r of matrix.txt) AND input."""
    o = 0
    for r in range(32):
        acc = 0
        row = MATRIX_ROWS[r]
        for c in range(32):
            if row[c] == "1" and (v >> c) & 1:
                acc ^= 1
        if acc:
            o |= 1 << r
    return o


def simulate_circuit(rel, v):
    """Genuine gate-by-gate replay: propagate real bit values, then read the
    signal that carries each output mask."""
    data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    mask = [1 << i for i in range(32)]
    val = [(v >> i) & 1 for i in range(32)]
    for a, b in data["gates"]:
        mask.append(mask[a] ^ mask[b])
        val.append(val[a] ^ val[b])
    where = {}
    for i, m in enumerate(mask):
        where.setdefault(m, i)
    o = 0
    for r in range(32):
        if SPEC[r] not in where:
            raise SystemExit(f"{rel}: output {r} not built")
        if val[where[SPEC[r]]]:
            o |= 1 << r
    return o


def main() -> int:
    args = parse_args("golden_vectors.txt")

    lines = []
    A = lines.append
    A("AES MixColumns (forward) — golden test vectors")
    A("=" * 78)
    A("")
    A("Target map: FIPS-197 sec. 5.1.3, one column, GF(2^8) with modulus 0x11B,")
    A("column polynomial [02 03 01 01] (circulant).  These vectors are the")
    A("normative acceptance test: a circuit that reproduces all of them under the")
    A("convention below is computing this project's MixColumns and no other.")
    A("")
    A("BYTE ORDER.  A column is four bytes s0 s1 s2 s3 printed left to right, s0")
    A("first.  out[col] = XOR_k coef[k] * in[(col+k) mod 4] with coef = 02 03 01 01.")
    A("")
    A("BIT INDEX CONVENTION (the one matrix.txt and every circuit file here use):")
    A("")
    A("    signal index j  =  8 * byte_number + bit_number,   0 <= j <= 31")
    A("    bit_number b of a byte is the coefficient of x^b  ->  LSB-FIRST")
    A("")
    A("  So input signal 0 is the LSB of byte 0; signal 7 is the MSB of byte 0;")
    A("  signal 24 is the LSB of byte 3.  Output signal r is read the same way:")
    A("  r = 8 * out_byte + out_bit.  A verifier that gets a byte-reversed or")
    A("  bit-reversed answer is in wrong_answers.md.")
    A("")
    A("Each vector is given three ways: as hex bytes, as the 32-bit vector in this")
    A("index convention (hex, bit j = signal j), and as the plain list of set")
    A("signal indices.")
    A("")
    A("=" * 78)
    A("")

    ok_matrix = True
    ok_circuit = True
    report = []
    for title, ib in VECTORS:
        iv = bytes_to_vec(ib)
        ov_spec = apply_spec_masks(iv)
        ov_mat = apply_matrix(iv)
        ov_cir = simulate_circuit(CIRCUIT, iv)
        ok_matrix &= (ov_mat == ov_spec)
        ok_circuit &= (ov_cir == ov_spec)
        report.append((title, ib, vec_to_bytes(ov_spec), ov_mat == ov_spec,
                       ov_cir == ov_spec))
        ob = vec_to_bytes(ov_spec)
        A(f"# {title}")
        A(f"  in  bytes : {' '.join('%02x' % b for b in ib)}")
        A(f"  out bytes : {' '.join('%02x' % b for b in ob)}")
        A(f"  in  vector: 0x{iv:08x}   set signals: {idx_list(iv)}")
        A(f"  out vector: 0x{ov_spec:08x}   set signals: {idx_list(ov_spec)}")
        A("")

    A("=" * 78)
    A("")
    A("MACHINE-READABLE FORM (one vector per line: in_hex4 out_hex4 in_u32 out_u32)")
    A("")
    for title, ib in VECTORS:
        iv = bytes_to_vec(ib)
        ov = apply_spec_masks(iv)
        A("  %s  %s  %08x %08x" % (
            "".join("%02x" % b for b in ib),
            "".join("%02x" % b for b in vec_to_bytes(ov)),
            iv, ov))
    A("")
    A("=" * 78)
    A("")
    A("HOW TO USE THESE")
    A("")
    A("  A circuit file in this project is a list of 2-input XOR gates over 32")
    A("  input signals.  To check it against a vector: set input signal j to bit j")
    A("  of the in vector, replay the gates in order, and read output r off the")
    A("  signal whose value -- the set of input bits it XORs together -- equals")
    A("  row r of matrix.txt.")
    A("")
    A("  That replay is control 2 of scripts/build_golden_vectors.py, which")
    A("  generates this file: it runs every vector below through")
    A(f"  {CIRCUIT}")
    A("  gate by gate, on concrete bits rather than symbolic values, and prints")
    A("  the transcript.  Re-run it yourself:")
    A("")
    A("      python3 scripts/build_golden_vectors.py --check")
    A("")
    A("  These vectors are a CONVENIENCE, not the proof.  Because the map is")
    A("  linear, the 32 basis vectors (unit inputs) already determine it")
    A("  completely; verify.py compares all 32 output values at once, which is")
    A("  why it is a proof of correctness and not a sample.  The FIPS-197")
    A("  column is here so an integrator can check agreement with the")
    A("  standard.")
    A("")
    A("  To check a circuit file of your own, including one this repository has")
    A("  never seen:")
    A("")
    A("      python3 verify.py --adhoc <your_file.json>")
    A("")

    rc = emit("golden_vectors.txt", "\n".join(lines).encode("utf-8"), args.check)

    print()
    print("CONTROL: each vector recomputed two independent ways")
    print(f"  circuit used for the simulation path: {CIRCUIT}")
    print(f"  {'input':<12} {'output':<12} via-matrix.txt  via-circuit-simulation")
    for title, ib, ob, m, c in report:
        print("  %-12s %-12s %-15s %s" % (
            " ".join("%02x" % b for b in ib), " ".join("%02x" % b for b in ob),
            "OK" if m else "MISMATCH", "OK" if c else "MISMATCH"))
    print()
    print("  FIPS-197 worked example db 13 53 45 -> 8e 4d a1 bc :",
          "CONFIRMED" if report[0][2] == [0x8E, 0x4D, 0xA1, 0xBC] else "MISMATCH")
    print("  matrix path  :", "PASS" if ok_matrix else "FAIL")
    print("  circuit path :", "PASS" if ok_circuit else "FAIL")
    return 0 if (ok_matrix and ok_circuit and rc == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
