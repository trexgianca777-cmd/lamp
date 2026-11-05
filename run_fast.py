#!/usr/bin/env python3
"""Fast Legal Lights document runner.

Same verdict semantics as verdict.py (3 passes, lamp rules in code,
quote verified as exact substring). Faster than run_document.py:
- strict + generous readers run in parallel per unit (adjudicator
  needs their outputs, so it still follows);
- units run concurrently (default 3 workers) with a small stagger
  between submissions, inside the free tier's demonstrated envelope;
- verdict.json is written per unit the moment it finishes, so
  results stream instead of waiting for the whole document;
- a unit whose exact text already has a verdict in a previous
  workdir is reused, never re-run.
Usage: run_fast.py --units <txt> --out <panel.json> --party landlord
       --workdir <dir> [--reuse-units <txt> --reuse-work <dir>]
       [--workers 3]
"""
import argparse, concurrent.futures, json, os, shutil, sys, threading, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verdict import call_swarm, extract_json, load_prompt  # noqa: E402

ORDER = {"red": 0, "amber": 1, "white": 2, "green": 3}


def build_verdict(clause, party, workdir):
    os.makedirs(workdir, exist_ok=True)
    sp = load_prompt("strict.txt") + clause
    gp = load_prompt("generous.txt") + clause
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fs = ex.submit(call_swarm, sp, os.path.join(workdir, "strict"))
        fg = ex.submit(call_swarm, gp, os.path.join(workdir, "generous"))
        strict = extract_json(fs.result())
        generous = extract_json(fg.result())
    sf, gf = bool(strict.get("flag")), bool(generous.get("flag"))
    if sf or gf:
        adj_prompt = (load_prompt("adjudicator.txt") + clause +
                      f"\nThe other party in this document is the {party}. " +
                      f"Address actions to them by that role." +
                      f"\nStrict reader: {json.dumps(strict)}"
                      f"\nGenerous reader: {json.dumps(generous)}")
        adj = extract_json(call_swarm(adj_prompt,
                                      os.path.join(workdir, "adjudicator")))
    else:
        # Lazy green: both readers clear, no adjudicator call needed.
        adj = {"skipped": True}
    if adj.get("unjudgeable"):
        lamp = "white"
    elif sf and gf:
        lamp = "red"
    elif sf or gf:
        lamp = "amber"
    else:
        lamp = "green"
    quote = adj.get("quote", "")
    v = {"clause": clause, "strict": strict, "generous": generous,
         "adjudicator": adj, "lamp": lamp, "plain": adj.get("plain", ""),
         "action": adj.get("action", ""), "quote": quote,
         "quote_valid": bool(quote) and quote in clause,
         "adjudicator_skipped": bool(adj.get("skipped")),
         "backend": "groq:openai/gpt-oss-20b", "meta_used": False,
         "cost": 0.0}
    with open(os.path.join(workdir, "verdict.json"), "w") as f:
        json.dump(v, f, indent=2)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--party", default="other party")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--reuse-units")
    ap.add_argument("--reuse-work")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()

    units = [u for u in (p.strip() for p in
                        open(a.units).read().split("\n\n"))
             if len(u) >= 40]
    # Reuse map: exact clause text -> finished verdict.json path.
    reuse = {}
    if a.reuse_units and a.reuse_work:
        old = [u for u in (p.strip() for p in
                           open(a.reuse_units).read().split("\n\n"))
               if len(u) >= 40]
        for i, text in enumerate(old):
            vpath = None
            for dirname in (f"unit-{i}", f"clause-{i}"):
                cand = os.path.join(a.reuse_work, dirname, "verdict.json")
                if os.path.exists(cand):
                    vpath = cand
                    break
            if vpath:
                reuse[text] = vpath

    os.makedirs(a.workdir, exist_ok=True)
    rows = [None] * len(units)
    failed = []
    lock = threading.Lock()

    def run_one(i, clause):
        d = os.path.join(a.workdir, f"unit-{i}")
        try:
            if clause in reuse:
                os.makedirs(d, exist_ok=True)
                src = reuse[clause]
                dst = os.path.join(d, "verdict.json")
                # Resume into the same workdir: source and target may
                # already be the same file; copying it onto itself is
                # an error, so just read it.
                if os.path.abspath(src) != os.path.abspath(dst):
                    shutil.copy(src, dst)
                with open(dst) as f:
                    v = json.load(f)
                v["reused"] = True
                with open(dst, "w") as f:
                    json.dump(v, f, indent=2)
            else:
                # Clean slate: a resumed unit must never read a previous
                # attempt's partial outputs as fresh ones.
                shutil.rmtree(d, ignore_errors=True)
                v = build_verdict(clause, a.party, d)
        except Exception as e:
            # One unit's failure must never kill the batch.
            err = {"index": i, "error": str(e)[:300]}
            with lock:
                failed.append(err)
            print(f"[{i}] ERROR :: {e}", flush=True)
            return None
        v["index"] = i
        with lock:
            rows[i] = v
        print(f"[{i}] {v['lamp'].upper()} :: {v['plain'][:90]}", flush=True)
        return v

    with concurrent.futures.ThreadPoolExecutor(
            max_workers=a.workers) as ex:
        futs = []
        for i, clause in enumerate(units):
            futs.append(ex.submit(run_one, i, clause))
            time.sleep(1.5)  # stagger submissions inside the safe envelope
        for f in concurrent.futures.as_completed(futs):
            f.result()

    rows = [r for r in rows if r is not None]
    rows.sort(key=lambda r: ORDER[r["lamp"]])
    counts = {lamp: sum(1 for r in rows if r["lamp"] == lamp)
              for lamp in ORDER}
    panel = {"counts": counts, "total": len(rows), "rows": rows,
             "failed": failed,
             "backend": "groq:openai/gpt-oss-20b", "meta_used": False}
    with open(a.out, "w") as f:
        json.dump(panel, f, indent=2)
    print(json.dumps(counts) + f" total={len(rows)} failed={len(failed)}"
          f" -> {a.out}")
    if failed:
        print("FAILED UNITS: " + json.dumps(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
