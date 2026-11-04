#!/usr/bin/env python3
"""Trial runner: run verdict.py over selected clauses, save verdicts.
Usage: python3 run_trial.py <trial-dir> <doc:clause-index,...>
Example: python3 run_trial.py trials/trial-1 lease:0,1,2 terms:0,1,2 ticket:0,1,2
Clause indexes follow run_document.split_clauses order (synthetic header skipped).
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from run_document import split_clauses

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    trial, spec = sys.argv[1], sys.argv[2]
    os.makedirs(trial, exist_ok=True)
    results = []
    for part in spec.split():
        doc, idxs = part.split(":")
        with open(os.path.join(ROOT, "samples", doc + ".txt")) as f:
            clauses = split_clauses(f.read())
        for i in [int(x) for x in idxs.split(",")]:
            d = os.path.join(trial, f"{doc}-{i}")
            if os.path.exists(os.path.join(d, "verdict.json")):
                print(f"{doc}-{i}: skipped (verdict exists, resume mode)")
                with open(os.path.join(d, "verdict.json")) as f:
                    v = json.load(f)
                v["doc"], v["clause_index"] = doc, i
                results.append(v)
                continue
            subprocess.run([sys.executable, os.path.join(ROOT, "verdict.py"),
                            "--clause", clauses[i], "--out", d],
                           check=True, capture_output=True, text=True)
            with open(os.path.join(d, "verdict.json")) as f:
                v = json.load(f)
            v["doc"], v["clause_index"] = doc, i
            results.append(v)
            print(f"{doc}-{i}: lamp={v['lamp']} quote_valid={v['quote_valid']}")
            import time; time.sleep(6)  # free-tier rate-limit guard
    with open(os.path.join(trial, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(f"saved {len(results)} verdicts -> {trial}/results.json")


if __name__ == "__main__":
    main()
