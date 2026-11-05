/* Lamp app. Document on the left, highlighted by lamp color.
   Detail card on the right. No framework, no build step. */
const $ = id => document.getElementById(id);
const LAMPS = {
  red:   { sym: '▲', label: 'Bad part' },
  amber: { sym: '◆', label: 'Careful part' },
  green: { sym: '●', label: 'Fine part' },
  white: { sym: '○', label: 'Not sure part' },
};
const esc = s => (s || '').replace(/[&<>"]/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* Same split as run_document.py: blank-line paragraphs, minus the
   synthetic-sample header and minus fragments under 40 chars. */
function splitClauses(text) {
  const paras = [], clauses = [];
  for (const raw of text.split(/\n\s*\n/)) {
    const p = raw.replace(/\s+/g, ' ').trim();
    if (!p) continue;
    paras.push(p);
    if (p.startsWith('SYNTHETIC SAMPLE')) continue;
    if (p.length < 40) continue;
    clauses.push(p);
  }
  return { paras, clauses };
}

function threat(panel) {
  const c = panel.counts;
  if (c.red > 0) return { word: 'Bad parts found', lamp: 'red' };
  if (c.amber > 0) return { word: 'Some parts need care', lamp: 'amber' };
  if (c.white > 0) return { word: 'Some parts unclear', lamp: 'white' };
  return { word: 'Looks fine', lamp: 'green' };
}

function countLine(panel) {
  const c = panel.counts, parts = [];
  if (c.red) parts.push(`${c.red} bad`);
  if (c.amber) parts.push(`${c.amber} careful`);
  if (c.white) parts.push(`${c.white} not sure`);
  if (c.green) parts.push(`${c.green} fine`);
  return parts.join(' · ') + ` · ${panel.total} parts total`;
}

function render(text, panel) {
  const t = threat(panel);
  $('threat').innerHTML =
    `<span class="dot ${t.lamp}"></span>${t.word}` +
    `<small>${countLine(panel)}</small>`;
  const { paras, clauses } = splitClauses(text);
  const byIndex = {};
  for (const r of panel.rows) byIndex[r.index] = r;
  let clausePos = -1;
  $('doc').innerHTML = paras.map(p => {
    if (p.startsWith('SYNTHETIC SAMPLE'))
      return `<p class="note">${esc(p)}</p>`;
    if (p.length < 40) return `<p>${esc(p)}</p>`;
    clausePos += 1;
    const row = byIndex[clausePos];
    /* Only problems get highlighted. Fine parts stay plain text. */
    if (!row || row.lamp === 'green') return `<p>${esc(p)}</p>`;
    const L = LAMPS[row.lamp];
    return `<p><mark class="${row.lamp}" data-index="${row.index}">` +
      `<span class="sym ${row.lamp}">${L.sym}</span>${esc(p)}</mark></p>`;
  }).join('');
  $('doc').querySelectorAll('mark').forEach(m => {
    m.onclick = () => {
      $('doc').querySelectorAll('mark').forEach(x => x.classList.remove('selected'));
      m.classList.add('selected');
      showDetail(byIndex[+m.dataset.index]);
    };
  });
  /* Open on the first problem, so the detail card is never empty. */
  const first = panel.rows.find(r => r.lamp === 'red')
    || panel.rows.find(r => r.lamp === 'amber')
    || panel.rows.find(r => r.lamp === 'white');
  if (first) {
    const m = $('doc').querySelector(`mark[data-index="${first.index}"]`);
    if (m) m.classList.add('selected');
    showDetail(first);
  } else {
    $('detail').innerHTML =
      `<p class="lamp-line"><span class="dot green"></span>Looks fine</p>` +
      `<p class="plain">No bad parts found in this document.</p>`;
  }
}

function showDetail(r) {
  const L = LAMPS[r.lamp];
  $('detail').innerHTML =
    `<p class="lamp-line"><span class="dot ${r.lamp}"></span>${L.sym} ${L.label.toUpperCase()}</p>` +
    `<p class="plain">${esc(r.plain)}</p>` +
    (r.action ? `<p class="action">Do this: ${esc(r.action)}</p>` : '') +
    `<details><summary>Show the original words</summary>` +
    `<p class="orig">${esc(r.clause)}</p>` +
    (r.quote_valid
      ? `<p class="quote">Quoted from your document: <q>${esc(r.quote)}</q></p>`
      : `<p class="warn">I could not match the original words for this part.</p>`) +
    `</details>`;
}

function setProgress(msg) { $('progress').textContent = msg; }

async function runLive() {
  const text = $('paste').value.trim();
  if (!text) { setProgress('Paste some words or drop a file first.'); return; }
  setProgress('Checking your document… this can take a minute.');
  try {
    const res = await fetch('/api/document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const panel = await res.json();
    if (panel.error) throw new Error(panel.error);
    render(text, panel);
    setProgress('');
  } catch (e) {
    setProgress('Checking is not available right now. Try again in a bit.');
  }
}

async function handlePdf(file) {
  setProgress('Reading your file…');
  try {
    const buf = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
    let text = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      setProgress(`Reading page ${i} of ${pdf.numPages}…`);
      const page = await pdf.getPage(i);
      const tc = await page.getTextContent();
      text += tc.items.map(it => it.str).join(' ') + '\n\n';
    }
    if (text.trim().length < 40) {
      setProgress('I could not read that file. It might be a photo of pages, not words. Try pasting the words instead.');
      return;
    }
    $('paste').value = text;
    runLive();
  } catch (e) {
    setProgress('I could not open that file. Try pasting the words instead.');
  }
}

$('run').onclick = runLive;
$('file').onchange = e => { if (e.target.files[0]) handlePdf(e.target.files[0]); };
const dropZone = document.querySelector('.filebtn');
dropZone.ondragover = e => e.preventDefault();
dropZone.ondrop = e => {
  e.preventDefault();
  if (e.dataTransfer.files[0]) handlePdf(e.dataTransfer.files[0]);
};
if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'assets/pdf.worker.min.js';
}
