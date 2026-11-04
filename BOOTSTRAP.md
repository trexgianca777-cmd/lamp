# BOOTSTRAP — Legal Lights, for a fresh Muse

You are looking at Legal Lights: a fine-print demystifier. Paste a legal
document or drop in a full PDF. Every clause gets a lamp: red costs you,
amber watch it, green standard, white unclear. Click a highlight to see
its plain meaning, one action, and quoted wording from the document.

## Run the demo (no keys, no server)

Open `index.html` in a browser, or serve this directory with any static
server. The three sample buttons load pre-generated panels from
`panels/`. No live calls happen in this mode.

## Run it live (needs the swarm)

```
source ~/workspace/freellmapi/vault/vault.sh && swarm_vault_load
python3 server.py        # then open http://localhost:8000/
```

The page then calls `/api/document`, which runs `run_document.py`, which
runs `verdict.py` per clause through `swarm-call.sh` (Groq gpt-oss-20b,
$0 free tier). The vault key never touches a file.

## File map

- `index.html`, `styles.css`, `app.js` — the app. Document on the left
  with inline highlights, detail card on the right, threat badge on top.
- `assets/pdf.min.js`, `assets/pdf.worker.min.js` — vendored Mozilla
  pdf.js. PDF text is extracted in the page; the file never uploads.
- `verdict.py` — the clause verdict unit (strict reader, generous
  reader, adjudicator; lamp rules in code; quote verified as an exact
  substring). `run_document.py` — runs it over a document.
  `prompts/` — the three exact prompts. `server.py` — stdlib server.
- `samples/` — synthetic sample documents (.txt and .pdf) plus
  pre-generated panels (`panel-*.json`). `panels/` — copies the app
  loads. `trials/` — trial runs and grades.
- `README.md` — full spec, verified counts, trial-grade log, limits.
  `DEMO.md` — 180-second demo script.

## Rules that stay true

- Never claim a Meta model is used. No Meta key is on disk. The
  adjudicator slot is built for Muse Spark; until a key lands, every
  output is labeled Groq and the page says so.
- Sample documents are synthetic and labeled. Never present one as real.
- Scanned image PDFs have no text layer; the page refuses them plainly
  instead of guessing. OCR is not built.
- Headings use Beata LP (LetterPerfect, commercial) via the hosted
  embed link in `index.html`. The font file is deliberately NOT in this
  repo. Body and document text stay in a plain legible face. A shipped
  product needs a LetterPerfect license for the font.
- Outputs are not legal advice.
