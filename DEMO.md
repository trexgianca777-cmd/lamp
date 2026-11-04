# Legal Lights — 180-second demo script

0-25s (problem): "Everybody signs things they have not read. Leases, terms
of service, fines. The fine print is where the money goes."
25-50s (input): Drop the sample lease PDF onto the page. Lamps fill in as
clauses are read: 4 red, 2 amber, 6 clauses total. No account, no setup.
The file never uploads; text is extracted in the page.
50-95s (the disagreement): "One clause, two readers. The strict reader
flags the auto-renewal clause, the generous reader clears it. The
adjudicator settles it and the lamp flips amber. That disagreement is
the product: one cheap read is not trusted alone."
95-125s (the action): Top red row: rent can rise with 30 days notice and
no cap. Action on screen: ask the landlord for a cap in writing. "That
is not a summary. That is the one thing to do before signing."
125-160s (second document): Load the sample terms panel: 2 red, 2 amber,
2 green. Red row: accounts inactive 12 months may be deleted, content
included. Green row for contrast: cancel anytime from Settings, then
Billing, then Cancel. Same engine, same lamps, different document.
160-180s (close): "Every lamp traces to quoted wording from your
document. Groq free tier, zero dollars, no Meta key yet. The adjudicator
slot is built for Muse Spark the day credits land."

Fallbacks if the live call dies on stage: the three demo buttons load
pre-generated panels from the repo (lease 4 red/2 amber, terms 2 red/
2 amber/2 green, ticket 2 red/1 amber). The demo never depends on a live
call succeeding, and a live full-document run takes ~2 minutes, so the
video uses the pre-generated panels. Scanned image PDFs are out of scope
tonight and the page says so instead of guessing.
