#!/usr/bin/env python3
"""Generate matrix.txt and matrix.sha256.

Nothing here is copied from a published table. The rows are emitted from
verify.py's own `mixcolumns_target_masks()`, so matrix.txt is by construction
the map the verifier checks every circuit against.

CONTROL: the same 32x32 matrix is rebuilt a second time from
audit/cleanroom_verify.py -- a separately written byte-level reference that
multiplies in GF(2^8) and never sees verify.py's masks -- and the two must
agree bit for bit.

    python3 scripts/build_matrix.py            # regenerate
    python3 scripts/build_matrix.py --check     # fail if the shipped files are stale
"""
import hashlib

from _builders import ROOT, emit, parse_args  # noqa: E402  (sys.path set there)

import verify  # noqa: E402
import audit.cleanroom_verify as cleanroom  # noqa: E402


def main() -> int:
    args = parse_args("matrix.txt and matrix.sha256")

    masks = verify.mixcolumns_target_masks()
    assert len(masks) == 32

    # row r, column c is 1 iff output bit r depends on input bit c.
    rows = ["".join("1" if (masks[r] >> c) & 1 else "0" for c in range(32))
            for r in range(32)]
    body = ("\n".join(rows) + "\n").encode("utf-8")
    digest = hashlib.sha256(body).hexdigest()

    rc = emit("matrix.txt", body, args.check)
    rc |= emit("matrix.sha256", f"{digest}  matrix.txt\n".encode("utf-8"), args.check)

    weights = sorted({r.count("1") for r in rows})
    profile = {w: sum(1 for r in rows if r.count("1") == w) for w in weights}
    print()
    print("sha256(matrix.txt):", digest)
    print("row weights:", profile, "(MixColumns is 20 weight-5 and 12 weight-7 rows)")

    print()
    print("CONTROL: rebuilt independently from audit/cleanroom_verify.py")
    indep = cleanroom.build_target_masks()
    same = indep == masks
    print("  cleanroom_verify.py agrees on all 32 output masks:", same)
    if not same:
        for r, (a, b) in enumerate(zip(masks, indep)):
            if a != b:
                print(f"    row {r}: verify.py {a:#010x} cleanroom {b:#010x}")
        return 1

    print("  transpose check (the map is not symmetric, so orientation is "
          "unambiguous):", rows != ["".join(r[c] for r in rows) for c in range(32)])
    if rc:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
