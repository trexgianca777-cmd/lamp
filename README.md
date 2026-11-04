# Legal Lights

Paste a legal document, or drop in a full PDF. Every clause gets a lamp:
red costs you, amber watch it, green standard, white unclear and needs a
human look. Reds first, then ambers, then white. Greens collapse.
Every lamp carries one plain sentence, one action, and quoted wording
from your document.

## The one thing

A clause verdict unit. Input: one clause. Output: plain line, lamp,
action, quote trace. Three passes, all Groq gpt-oss-20b on the $0 free
tier: a strict reader, a generous reader, and an adjudicator who settles
disagreements. Lamp rules live in code, not in the model: both flag is
red, disagreement is amber, both clear is green, adjudicator says
unjudgeable is white. The engine is this unit run over every clause,
with lamps aggregated into the panel.

## The app (new)

`index.html` + `styles.css` + `app.js` is the demo app. Document on the
left with inline highlights in lamp colors, each clause marked with its
symbol (▲ red, ◆ amber, ● green, ○ white). Threat badge on top: HIGH
if any red, ELEVATED if any amber and no red, UNCLEAR if any white and
no red or amber, CLEAR if all green. Click a highlight for the detail
card: plain meaning, action, original wording, quoted trace.

Deploy paths:

- GitHub Pages: publish this directory. The sample buttons and
  pre-generated panels work with no server and no keys.
- Live mode: `python3 server.py` (vault-loaded shell) enables paste,
  PDF drop, and full-document runs through the swarm.

Headings use Beata LP (LetterPerfect) via the hosted embed link in
`index.html`. Beata LP is a commercial font ($39, LetterPerfect); the
font file is deliberately not vendored into this repo, and the hosted
embed is a preview path. Body and document text stay in a plain legible
face on purpose: Beata LP is caps and small caps, wrong for body text.
A shipped product needs a LetterPerfect license for the font.

## Run it

```
source ~/workspace/freellmapi/vault/vault.sh && swarm_vault_load
python3 server.py        # then open http://localhost:8000/
```

No server needed for the samples: the demo buttons load pre-generated
panels from `samples/panel-*.json` when the server is unreachable.

CLI:

```
python3 verdict.py --clause "clause text" --out <dir> [--party landlord]
python3 run_document.py --doc <txt> --out <panel.json> [--party landlord]
```

## Files

- `verdict.py`, `run_document.py`, `server.py` (stdlib only)
- `index.html`, `assets/pdf.min.js`, `assets/pdf.worker.min.js`
  (vendored Mozilla pdf.js 3.11.174; PDF text is extracted in the page,
  the file itself never uploads)
- `prompts/strict.txt`, `prompts/generous.txt`, `prompts/adjudicator.txt`
- `samples/lease.txt`, `samples/terms.txt`, `samples/ticket.txt` and
  matching `.pdf` files (LibreOffice-generated, text layer verified with
  pdftotext). All samples are synthetic and labeled as such.
- `samples/panel-lease.json`, `panel-terms.json`, `panel-ticket.json`
  (pre-generated with the final prompts)
- `trials/` — trial runs, grades, and the fixes they caused
- `DEMO.md` — 90-second demo script

## Verified panel counts (final prompts, live runs)

- Lease, 6 clauses: red 4, amber 2, white 0, green 0
- Terms, 6 clauses: red 2, amber 2, white 0, green 2
- Ticket, 3 clauses: red 2, amber 1, white 0, green 0
- All 15 rows: quote verified as an exact substring of its clause.

## Trial-grade log (3 cycles + 1 fix cycle, all live, $0)

- Trial 1: 6/9 clauses, then HTTP 429 from the Groq free tier after ~21
  rapid calls. Fixed: retry backoff in `verdict.py`, resume mode and a 6s
  stagger in the runners.
- Trial 1b: 9/9, 9/9 quotes valid. Found a vague action and a missed
  personal-data flag. Fixed: concrete-action rule, "personal data" added
  to the cost list.
- Trial 2: found an action instructing acceptance of a trap, and a $25
  misread ($75 minus $25 is $50, not $25). Fixed: protective-action rule
  and an amounts rule in the adjudicator prompt. Both re-verified.
- Trial 2 fix: an "ask the reader" agency slip fixed by addressing
  actions to the user directly, re-verified. Cycle 4: party roles
  (landlord/company/issuer) added after panels called a landlord "the
  company"; panels regenerated and verified.

## Hackathon mapping (honest)

- Impact: a real product; every lamp is a decision a person acts on.
- Demo: one screen, drop a PDF, lamps fill in, one disagreement shown.
- Technical Depth: disagreement mechanics plus a quote trace per lamp.
- Meta Tooling: EMPTY as of now. No Meta model is used, because no Meta
  key is on disk and credits have not landed. The adjudicator slot is
  built for Muse Spark: adjudicate disagreements only, so Meta spend
  stays tiny when a key exists. Until then every output is labeled Groq
  and no Meta claim is made anywhere in the product or the video.
- New-work rule: the unit, the panel, and the prompts are built
  2026-11-04 (event week). The swarm underneath is labeled foundation.

## Limits, stated plainly

- Scanned image PDFs have no text layer; the page says so and asks for
  pasted text instead of guessing. OCR is not built.
- Clause splitting is paragraphs separated by blank lines, minus
  fragments under 40 characters. Real-world documents with unusual
  formatting will split imperfectly.
- Actions sometimes propose a reader-set deadline (for example "within
  10 days"). That is a recommendation from the adjudicator, not a term
  from the clause. Plain lines state only clause facts.
- Some plain lines echo the clause closely when the clause is already
  plain. Accurate, low transformation; recorded, not hidden.
- Outputs are not legal advice. The page and the panels carry no legal
  claim, and no sample document is real.
- Full-document runs are slow by design: 3 live calls per clause plus a
  6s stagger against the free-tier rate limit. A 6-clause document takes
  roughly 2 minutes live; the pre-generated panels exist so the demo
  never waits on that.
