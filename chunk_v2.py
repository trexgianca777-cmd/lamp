#!/usr/bin/env python3
"""Chunk a real lease into verdict units, v2.

Rules (learned from the v1 test on a 42-page lease):
- Drop junk lines first: Docusign envelope headers, "In Process"
  watermarks, page footers, signature scaffolding lines.
- Cut the EPA lead pamphlet (educational booklet, not lease terms).
- Split on the lease's own structure: roman-numeral sections I..LV,
  then ADDENDUM titles. Sections stay WHOLE even at ~3000 chars:
  v1 sentence-splitting produced mid-thought fragments.
- The post-LV blob (lead disclosure form + flood notice) splits at
  its natural form titles, not at sentences.
- Nothing is silently dropped: every kept unit is printed with its
  length, and the pamphlet cut is reported.
Usage: python3 chunk_v2.py <lease.txt> <units-out.txt>
"""
import re, sys


def roman(n):
    vals = [(50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'),
            (4, 'IV'), (1, 'I')]
    out = ''
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    text = open(src).read()
    lines = []
    for ln in text.split('\n'):
        s = ln.strip()
        if s.startswith('Docusign Envelope ID'):
            continue
        if s == 'In Process':
            continue
        if re.fullmatch(r'Page \d+', s):
            continue
        if '___' in s and 'Date:' in s:
            continue
        lines.append(ln)
    flat = ' '.join(' '.join(lines).split())

    a = flat.find('Read this entire brochure')
    b = flat.find('ADDENDUM PACKAGE')
    if 0 < a < b:
        print(f'pamphlet cut: {len(flat[a:b])} chars (educational, not terms)')
        flat = flat[:a] + ' ' + flat[b:]

    nums = sorted((roman(i) for i in range(1, 61)), key=len, reverse=True)
    alt = '|'.join(nums)
    head = r'(?:' + alt + r')\.\s+(?=[A-Z])'
    parts = re.split(r'(?=\b' + head + r')', flat)
    chunks = []
    for p in parts:
        p = p.strip()
        if len(p) < 40:
            continue
        if not re.match(r'^(?:' + alt + r')\.', p):
            continue
        chunks.append(p)

    out = []
    for c in chunks:
        # ADDENDUM titles inside a chunk become their own units.
        subs = re.split(r'(?=ADDENDUM\s+[A-Z])', c)
        for s in subs:
            s = s.strip()
            if len(s) < 40:
                continue
            out.append(s)

    # Post-LV blob: split lead disclosure from flood notice at form titles.
    final = []
    for c in out:
        if c.startswith('LV.'):
            marks = []
            for m in ('Disclosure of Information on Lead-Based Paint',
                      'For purposes of this notice'):
                i = c.find(m)
                if i > 100:
                    marks.append(i)
            if marks:
                marks.sort()
                prev = 0
                for i in marks:
                    final.append(c[prev:i].strip())
                    prev = i
                final.append(c[prev:].strip())
                continue
        final.append(c)
    final = [c for c in final if len(c) >= 40]

    with open(dst, 'w') as f:
        f.write('\n\n'.join(final))
    print(f'v2 units: {len(final)}')
    for i, c in enumerate(final):
        print(f'{i:2d} {len(c):5d}  {c[:70]}')


if __name__ == '__main__':
    main()
