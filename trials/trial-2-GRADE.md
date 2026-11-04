# Trial-2 grade (after cycle-3 fixes) — 2026-11-04, live Groq gpt-oss-20b, $0
Scope: 2 failing clauses rerun + 2 regression checks, then 1 agency fix rerun.

- terms-0 amber: FIXED. Action now protective: written notice + deadline to
  review or opt out. Note: the "30 days" in the action is the reader's own
  proposed deadline (advice), not a clause term; plain line states no numbers
  beyond the clause. Acceptable, noted.
- ticket-0 red: FIXED. Plain no longer restates the reduction as a final
  amount: "$75 fine... a $25 reduction applies." The $50 result is not
  computed explicitly, but the material misstatement is gone.
- lease-0 red: PASS, no regression. Accurate, specific.
- terms-2 amber: agency slip in trial-2 ("Ask the reader..."), fixed by a
  prompt line (address the action to the user directly) and verified in
  trial-2fix: "Ask the company to provide a detailed privacy notice...
  and request an option to opt out." PASS.

Trial-grade loop status after 3 cycles: 0 open failures on the 9-clause
trial set. Remaining known blemishes (not failures): lease-2 red is slightly
harsh for yard upkeep; ticket-0 plain does not compute $50 explicitly;
terms-0 action proposes a reader-set deadline. All recorded, none hidden.
Next: full-document panels for the demo page.
