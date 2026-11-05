#!/usr/bin/env python3
"""Lamp clause verdict unit. One clause in, one lamp out.

Passes (all Groq gpt-oss-20b on the $0 free tier, no Meta calls):
  1. strict reader    -> flag bool
  2. generous reader  -> flag bool
  3. adjudicator      -> plain line, action, exact quote, unjudgeable bool
Lamp rules applied in code, not by the model:
  both flag -> red; disagree -> amber; both clear -> green;
  adjudicator says unjudgeable -> white.
The quote is verified as an exact substring of the clause; a non-matching
quote is recorded as quote_valid=false, never silently fixed.
Usage: python3 verdict.py --clause "text" --out <dir>
       python3 verdict.py --clause-file <file> --out <dir>
Writes verdict.json plus raw model outputs into <dir>.
"""
import argparse, glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SWARM = os.path.expanduser("~/workspace/freellmapi/swarm-call.sh")
MODEL = "openai/gpt-oss-20b"


def load_prompt(name):
    with open(os.path.join(HERE, "prompts", name)) as f:
        return f.read()


def call_swarm(prompt, outdir):
    env = dict(os.environ)
    env.update({
        "SWARM_MODELS": MODEL,
        "SWARM_PRESET": "short",
        "SWARM_CACHE": "0",
        "SWARM_TEMPERATURE": "0.2",
        "SWARM_FALLBACK": "",
    })
    last_err = None
    for attempt in range(4):
        r = subprocess.run([SWARM, prompt, outdir], env=env,
                           capture_output=True, text=True, timeout=180)
        txts = [p for p in glob.glob(os.path.join(outdir, "*.txt"))
                if os.path.basename(p) != "prompt.txt"]
        if txts:
            with open(txts[0]) as f:
                return f.read()
        # Free-tier 429s are transient: back off and retry instead of crashing.
        import time
        last_err = f"rc={r.returncode}"
        time.sleep(30 * (attempt + 1))
    raise RuntimeError(f"swarm-call produced no output text after retries "
                       f"({last_err})")


def extract_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON object in model output: {text[:300]}")
    return json.loads(m.group(0))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--clause")
    g.add_argument("--clause-file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--party", default="other party")
    a = ap.parse_args()
    clause = a.clause if a.clause else open(a.clause_file).read().strip()
    os.makedirs(a.out, exist_ok=True)

    strict = extract_json(call_swarm(load_prompt("strict.txt") + clause,
                                     os.path.join(a.out, "strict")))
    generous = extract_json(call_swarm(load_prompt("generous.txt") + clause,
                                       os.path.join(a.out, "generous")))
    sf, gf = bool(strict.get("flag")), bool(generous.get("flag"))
    if sf or gf:
        adj_prompt = (load_prompt("adjudicator.txt") + clause +
                      f"\nThe other party in this document is the {a.party}. " +
                      f"Address actions to them by that role." +
                      f"\nStrict reader: {json.dumps(strict)}"
                      f"\nGenerous reader: {json.dumps(generous)}")
        adj = extract_json(call_swarm(adj_prompt,
                                      os.path.join(a.out, "adjudicator")))
    else:
        # Lazy green: both readers clear. No adjudicator call is needed;
        # green units are shown as counts only, never in detail.
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
    verdict = {
        "clause": clause,
        "strict": strict, "generous": generous, "adjudicator": adj,
        "lamp": lamp,
        "plain": adj.get("plain", ""),
        "action": adj.get("action", ""),
        "quote": quote,
        "quote_valid": bool(quote) and quote in clause,
        "adjudicator_skipped": bool(adj.get("skipped")),
        "backend": f"groq:{MODEL}",
        "meta_used": False,
        "cost": 0.0,
    }
    with open(os.path.join(a.out, "verdict.json"), "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
