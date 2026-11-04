#!/usr/bin/env python3
"""Run the clause verdict unit over every clause in a document.

Clause splitting for tonight is deliberately simple and documented as a
limit: paragraphs separated by blank lines, minus the synthetic-sample
header line and minus fragments under 40 characters.
Usage: python3 run_document.py --doc <txt> --out <panel.json>
Writes panel JSON: counts, rows sorted red, amber, white, green.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = {"red": 0, "amber": 1, "white": 2, "green": 3}


def split_clauses(text):
    out = []
    for para in text.split("\n\n"):
        p = " ".join(para.split())
        if not p or p.startswith("SYNTHETIC SAMPLE"):
            continue
        if len(p) < 40:
            continue
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--party", default="other party")
    ap.add_argument("--workdir", default=None)
    a = ap.parse_args()
    with open(a.doc) as f:
        text = f.read()
    clauses = split_clauses(text)
    work = a.workdir or os.path.splitext(a.out)[0] + "-work"
    os.makedirs(work, exist_ok=True)
    rows = []
    for i, clause in enumerate(clauses):
        d = os.path.join(work, f"clause-{i}")
        subprocess.run([sys.executable, os.path.join(HERE, "verdict.py"),
                        "--clause", clause, "--out", d, "--party", a.party],
                       check=True, capture_output=True, text=True)
        with open(os.path.join(d, "verdict.json")) as f:
            v = json.load(f)
        v["index"] = i
        rows.append(v)
        import time; time.sleep(6)  # free-tier rate-limit guard
    rows.sort(key=lambda r: ORDER[r["lamp"]])
    counts = {lamp: sum(1 for r in rows if r["lamp"] == lamp)
              for lamp in ORDER}
    panel = {"counts": counts, "total": len(rows), "rows": rows,
             "backend": "groq:openai/gpt-oss-20b", "meta_used": False}
    with open(a.out, "w") as f:
        json.dump(panel, f, indent=2)
    print(json.dumps(counts) + f" total={len(rows)} -> {a.out}")


if __name__ == "__main__":
    main()
