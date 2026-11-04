# Trial-1b grade (after cycle-2 fixes) — 2026-11-04, live Groq gpt-oss-20b, $0
9/9 clauses completed, 9/9 quotes valid, no crashes (retry + stagger worked).
Fixes verified: terms-2 green -> amber (personal-data prompt change worked);
no 429 crash across 27 live calls in ~112s.

- lease-0 red: PASS. Accurate, specific action.
- lease-1 amber: PASS. Accurate, specific action.
- lease-2 red (was amber): PASS with note. Both readers now flag the violation
  consequence; slightly harsh for yard upkeep, but rule-consistent.
- terms-0 amber: FAIL G3. Action regressed to "Continue using the service to
  accept the updated terms" — concrete but wrong-direction: it instructs
  acceptance of the trap. The concrete-action instruction backfired.
- terms-1 green: PASS.
- terms-2 amber (was green): PASS. Fix verified; action specific.
- ticket-0 red: FAIL G1/G5. Plain misreads the deal: "paying within 14 days
  will reduce the fine to $25." The clause says a $25 reduction, so the
  result is $75 minus $25 equals $50, not $25. Material $25 error on a fine.
- ticket-1 amber: PASS. Accurate, specific action.
- ticket-2 red: PASS with note. Plain accurate; action wordy but specific.

Fixes applied for trial-2 (adjudicator prompt only):
1. Action must protect the reader (ask, deadline, opt out, cancel, document,
   dispute); never instruct acceptance of the term.
2. Amounts rule: state original and resulting amounts separately with the
   arithmetic shown; never restate a reduction as a final amount.
Trial-2 scope: rerun the 2 failing clauses (terms-0, ticket-0) plus regression
checks on 2 passing clauses (lease-0, terms-2).
