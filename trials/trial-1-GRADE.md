# Trial 1 grade (baseline, before fixes) — 2026-11-04, live Groq gpt-oss-20b, $0
Criteria: G1 plain accurate, G2 lamp justified, G3 action specific,
G4 quote exact substring (automated), G5 valid JSON no invented facts,
G6 demo renders, G7 hackathon honesty (Groq labeled, no Meta claim).
6 of 9 clauses completed; ticket-0/1/2 unrun (see failure note).

- lease-0 red: PASS all. Plain accurate, action specific, quote valid.
- lease-1 amber (strict T, generous F): PASS. Auto-renewal trap, disagreement honestly yields amber, action specific.
- lease-2 amber (strict F, generous T): PASS with note. Reader disagreement direction inverted vs expectation; lamp rule is direction-agnostic, which is the correct robustness property.
- terms-0 amber (strict T, generous F): PARTIAL G3. Action "Check whether the changes affect your rights" is vague.
- terms-1 green: PASS all. Cancel path plain and specific.
- terms-2 green (both clear): PARTIAL G2. Anonymized data sharing cleared by both readers; strict reader should have flagged a personal-data cost.

Failure (infrastructure, not quality): ticket-0 generous pass hit HTTP 429
after ~21 calls in ~18 seconds (Groq free-tier per-minute limit, server log:
"tpm/tpd-limit"). verdict.py crashed instead of backing off; runner had no
resume mode. Both are fixed in cycle 2.

Fixes applied for trial-1b:
1. verdict.py: retry loop on empty output, 30s/60s/90s backoff, up to 4 attempts.
2. run_trial.py: resume mode (skip clauses with verdict.json) + 6s stagger.
3. run_document.py: 6s stagger between clauses.
4. strict/generous prompts: cost list now includes "personal data".
5. adjudicator prompt: action must name a concrete step, place, or question, never "check whether".
