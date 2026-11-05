# Legal Lights — submission package

Copy-paste this into the hackathon submission form. Video file:
`demo.mp4` (attached in chat, also in this repo root after push).

## Title

Legal Lights

## Tagline

Fine print, lit up.

## Description

Legal Lights reads a lease, terms of service, or ticket and lights up
the bad parts. Paste text or drop a PDF on one screen. Every clause
gets a lamp: red means genuinely harmful or unusual, amber means the
readers disagreed and it is worth a look, green means standard or
fine, white means unclear and needs a human look. Click a highlight
for the plain meaning, what to do (only when something useful can be
done), and the original wording quoted word-for-word.

How it works: two readers check every clause. The strict reader casts
a wide net. The generous reader acts as a harsh filter: it flags only
genuinely harmful or unusual terms and never flags standard lease
terms (pet rules, smoking bans, guest limits, noise rules, ordinary
fees). An adjudicator settles flagged clauses only; when both readers
clear a clause it goes green with no extra call. Lamp rules live in
code, not in the model. Every quote is verified programmatically as an
exact substring of the clause; a non-matching quote is recorded as a
failure, never silently fixed.

Built during the event (November 4, 2026): the app, the prompts, the
fast runner, the chunker, and the demo video. The swarm underneath
is labeled foundation, not event work.

## Links

- Live product (UI; lamps need the live server):
  https://trexgianca777-cmd.github.io/legal-lights/
- Code (public repo): https://github.com/trexgianca777-cmd/legal-lights
- Demo video: upload `demo.mp4` from this repo root.

## Try it

1. Open the live product link, paste a lease or terms, press
   "Check my document".
2. Or run it live: `python3 server.py` in a vault-loaded shell, open
   http://localhost:8000/, drop a real PDF.
3. The video shows a real run on real clauses from a real 42-page
   lease: late fee, abandonment, quiet hours, pets, parties.

## Honest Meta note (read before judging Meta Tooling)

No Meta model call has run yet: no Meta key is on disk and the $150
credits applied for had not landed by submission time. All demo runs
are Groq gpt-oss-20b on the $0 free tier, labeled as such everywhere.
The adjudicator slot is built for Muse Spark (one call swap, costed
at fractions of a cent per document in the code comments), so the
Meta wiring is ready the moment a key lands. Nothing in this
submission claims a Meta run that did not happen.

## Test evidence (real, not samples)

- Full 42-page real lease, 66 clauses, run live in three batches
  under the first-pass filter: 24 red, 15 amber, 27 green, 0 white.
  A second pass under the harsher filter re-ran the same 66 clauses;
  its completed batches are in the repo workdirs and the final
  counts ship with the video description.
- Quote verification: 64 of 66 quotes verified as exact substrings
  on the first pass; the 2 failures are recorded, not hidden.
- No sample documents ship in the app. Verification is live only.
