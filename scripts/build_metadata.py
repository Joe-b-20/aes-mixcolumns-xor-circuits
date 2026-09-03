#!/usr/bin/env python3
"""Generate circuits_metadata.csv from the circuit files' own bytes.

Every column is computed by replaying each gate list: nothing is copied out of
bounds.json, and bounds.json is read only afterwards, as a control, to check
that the computed gate counts, depths and file hashes agree with what this
repository already claims.

Two of the columns need a definition, since a CSV header has no room for one:

  B           the number of gates whose mask is not one of the 32 MixColumns
              output masks and that at least one later gate consumes -- the
              "middle" of the circuit. It is NOT a lower bound; the collision
              with the 56-gate lower bound in README.md is arithmetic, since
              for a circuit with no dead and no duplicated gates B = gates - 32.
  expected_B  gates - 32, i.e. what B must equal when every gate is live and
              every output mask is produced exactly once. B != expected_B on a
              circuit means a deletable gate; see the B = 56 tripwire in the
              method repository (corpus/tripwire_demo/).

    python3 scripts/build_metadata.py            # regenerate
    python3 scripts/build_metadata.py --check     # fail if stale
"""
import csv
import hashlib
import io
import json

from _builders import ROOT, emit, parse_args  # noqa: E402

import verify  # noqa: E402

SPEC = verify.mixcolumns_target_masks()
TSET = set(SPEC)

COLS = ["id", "file", "sha256_file", "gates", "inputs", "depth",
        "depth_outputs", "outputs_built", "outputs_at_max_depth",
        "output_depth_histogram", "level_profile", "max_fanout_gate",
        "max_fanout_input", "fanout_histogram_gates",
        "fanout_histogram_inputs", "duplicate_masks", "dead_gates", "B",
        "expected_B", "declared_outputSignals", "declared_matches_computed"]


def histogram(values):
    h = {}
    for v in values:
        h[v] = h.get(v, 0) + 1
    return " ".join("%d:%d" % (k, h[k]) for k in sorted(h))


def analyse(raw):
    data = json.loads(raw)
    gates = [list(g) for g in data["gates"]]
    n = len(gates)
    n_in = data.get("inputCount", 32)

    mask = [1 << i for i in range(n_in)]
    depth = [0] * n_in
    fanout = [0] * n_in
    for a, b in gates:
        mask.append(mask[a] ^ mask[b])
        depth.append(max(depth[a], depth[b]) + 1)
        fanout.append(0)
        fanout[a] += 1
        fanout[b] += 1

    first = {}
    for i, m in enumerate(mask):
        first.setdefault(m, i)
    out_sig = [first[t] for t in SPEC if t in first]
    out_depths = [depth[s] for s in out_sig]

    declared = data.get("outputSignals")
    D_all = max(depth)
    D_out = max(out_depths) if out_depths else 0

    g_fan = fanout[n_in:]
    i_fan = fanout[:n_in]

    dead = sum(1 for k in range(n)
               if fanout[n_in + k] == 0 and mask[n_in + k] not in TSET)
    dup = n - len(set(mask[n_in:]))
    B = sum(1 for k in range(n)
            if mask[n_in + k] not in TSET and fanout[n_in + k] > 0)

    return {
        "gates": n,
        "inputs": n_in,
        "depth": D_all,
        "depth_outputs": D_out,
        "outputs_built": len(out_sig),
        "outputs_at_max_depth": sum(1 for d in out_depths if d == D_out),
        "output_depth_histogram": histogram(out_depths),
        "max_fanout_gate": max(g_fan) if g_fan else 0,
        "max_fanout_input": max(i_fan) if i_fan else 0,
        "fanout_histogram_gates": histogram(g_fan),
        "fanout_histogram_inputs": histogram(i_fan),
        "level_profile": histogram(depth[n_in:]),
        "duplicate_masks": dup,
        "dead_gates": dead,
        "B": B,
        "expected_B": n - 32,
        "declared_outputSignals": "yes" if declared else "no",
        "declared_matches_computed":
            ("n/a" if not declared
             else ("yes" if [mask[s] for s in declared] == SPEC else "NO")),
    }


def main() -> int:
    args = parse_args("circuits_metadata.csv")

    recs = []
    for path in sorted((ROOT / "circuits").glob("*.json")):
        raw = path.read_bytes()
        r = analyse(raw)
        r["id"] = path.stem
        r["file"] = path.relative_to(ROOT).as_posix()
        r["sha256_file"] = hashlib.sha256(raw).hexdigest()
        recs.append(r)

    recs.sort(key=lambda r: (r["gates"], r["depth"]))

    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=COLS)
    w.writeheader()
    for r in recs:
        w.writerow({k: r[k] for k in COLS})
    rc = emit("circuits_metadata.csv", buf.getvalue().encode("utf-8"), args.check)

    print()
    print("%-42s %5s %5s %6s %8s %10s" %
          ("id", "gates", "depth", "d_out", "maxfanout", "B/expect"))
    for r in recs:
        print("%-42s %5d %5d %6d %8d %10s" %
              (r["id"], r["gates"], r["depth"], r["depth_outputs"],
               r["max_fanout_gate"], "%d/%d" % (r["B"], r["expected_B"])))

    print()
    print("CONTROL 1: every circuit builds all 32 MixColumns outputs "
          "(target rebuilt by verify.py, not read from the file)")
    bad = [r["id"] for r in recs if r["outputs_built"] != 32]
    print("  32/32 outputs built:",
          "ALL %d PASS" % len(recs) if not bad else "FAIL: " + ", ".join(bad))

    print()
    print("CONTROL 2: computed values vs the repository's own bounds.json")
    bj = json.loads((ROOT / "bounds.json").read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in bj["circuits"]}
    disagree = []
    covered = 0
    for r in recs:
        c = by_id.get(r["id"])
        if not c:
            disagree.append("%s: not listed in bounds.json" % r["id"])
            continue
        covered += 1
        if c["gateCount"] != r["gates"]:
            disagree.append("%s: gateCount %s vs computed %d"
                            % (r["id"], c["gateCount"], r["gates"]))
        if c["depth"] != r["depth"]:
            disagree.append("%s: depth %s vs computed %d"
                            % (r["id"], c["depth"], r["depth"]))
        if c.get("sha256_circuit_json") != r["sha256_file"]:
            disagree.append("%s: sha256_circuit_json %s... vs computed %s..."
                            % (r["id"], str(c.get("sha256_circuit_json"))[:12],
                               r["sha256_file"][:12]))
    print("  %d/%d circuits found in bounds.json" % (covered, len(recs)))
    print("  disagreements:", "NONE" if not disagree else "")
    for d in disagree:
        print("    -", d)

    print()
    print("CONTROL 3: declared outputSignals resolve to the 32 target masks in order")
    for r in recs:
        if r["declared_outputSignals"] == "yes":
            print("  %-42s %s" % (r["id"], r["declared_matches_computed"]))

    return 0 if (not bad and not disagree and rc == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
