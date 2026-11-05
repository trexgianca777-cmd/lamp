#!/usr/bin/env python3
"""Render the Lamp demo video, v2: styled, no repetition.

165 seconds, 1280x720, 24fps. Animated frames piped to ffmpeg.
Demo data comes from /tmp/video-demo.json: real model verdicts on
real lease clauses (verified batch-3 panel rows). Nothing is mocked.
v2 changes: gradient background, glass cards, staggered title,
document lines that draw on with only the bad lines flashing red,
green shown as a counts-only chip (as in the app, never detail),
a sweeping lamp on the end card instead of repeating the title trio,
and a narration script that names verdicts instead of reading the
cards aloud.
"""
import json, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
INK = (242, 240, 234)
MUTED = (150, 150, 150)
RED = (229, 72, 77)
AMBER = (245, 166, 35)
GREEN = (70, 167, 88)
WHITE = (216, 216, 216)
CARD = (26, 29, 36, 255)
CARD2 = (35, 38, 46, 255)
LAMPWORD = {'red': ('BAD', RED), 'amber': ('CAREFUL', AMBER),
            'green': ('FINE', GREEN), 'white': ('NOT SURE', WHITE)}

FD = '/usr/share/fonts/truetype/dejavu/'


def font(name, size):
    try:
        return ImageFont.truetype(FD + name, size)
    except Exception:
        return ImageFont.load_default()


F_TITLE = font('DejaVuSans-Bold.ttf', 96)
F_BIG = font('DejaVuSans-Bold.ttf', 54)
F_MED = font('DejaVuSans-Bold.ttf', 38)
F_BODY = font('DejaVuSans.ttf', 30)
F_SMALL = font('DejaVuSans.ttf', 24)

_cache = {}
_grad = None


def bg_image():
    global _grad
    if _grad is None:
        col = Image.new('RGBA', (1, H))
        for y in range(H):
            f = y / H
            col.putpixel((0, y), (int(22 - 9 * f), int(24 - 9 * f),
                                  int(32 - 14 * f), 255))
        _grad = col.resize((W, H))
    return _grad.copy()


def text_img(text, fnt, color):
    key = (text, fnt, color)
    if key not in _cache:
        tmp = Image.new('RGBA', (10, 10))
        d = ImageDraw.Draw(tmp)
        box = d.textbbox((0, 0), text, font=fnt)
        w, h = box[2] - box[0] + 4, box[3] - box[1] + 4
        img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((2 - box[0], 2 - box[1]), text, font=fnt, fill=color + (255,))
        _cache[key] = img
    return _cache[key]


def paste(img, timg, x, y, alpha=255):
    if alpha < 255:
        timg = timg.copy()
        timg.putalpha(timg.getchannel('A').point(lambda a: a * alpha // 255))
    img.alpha_composite(timg, (int(x), int(y)))


def center(img, timg, y, alpha=255):
    paste(img, timg, (W - timg.width) // 2, y, alpha)


def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if font_measure(trial, fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def font_measure(text, fnt):
    tmp = Image.new('RGBA', (10, 10))
    d = ImageDraw.Draw(tmp)
    return d.textlength(text, font=fnt)


def lamp(img, cx, cy, r, color, pulse):
    d = ImageDraw.Draw(img)
    for k, a in ((2.6, 26), (1.9, 55), (1.4, 100)):
        rr = r * k * (0.9 + 0.1 * pulse)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,))
    d.ellipse([cx - r * 0.35, cy - r * 0.4, cx - r * 0.05, cy - r * 0.1],
              fill=(255, 255, 255, 90))


def fade(t, t0, t1):
    if t < t0:
        return 0.0
    if t > t1:
        return 1.0
    return (t - t0) / (t1 - t0)


# ---------------- scenes ----------------

def scene_title(img, t):
    d = ImageDraw.Draw(img)
    word = 'LAMP'
    widths = [font_measure(ch, F_TITLE) for ch in word]
    total = sum(widths) + 14 * (len(word) - 1)
    x = (W - total) // 2
    for i, ch in enumerate(word):
        a = int(fade(t, 0.2 + i * 0.07, 0.7 + i * 0.07) * 255)
        if ch != ' ':
            paste(img, text_img(ch, F_TITLE, INK), x, 220, a)
        x += widths[i] + 14
    uw = min(max((t - 1.2) / 1.0, 0.0), 1.0) * 360
    d.rectangle([(W - 360) // 2, 360, (W - 360) // 2 + uw, 368],
                fill=RED + (255,))
    import math
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    for i, c in enumerate((RED, AMBER, GREEN)):
        lamp(img, 490 + i * 150, 430, 42, c, pulse if i == int(t * 1.5) % 3 else 0.2)
    center(img, text_img('Demystify cryptic documents.', F_MED, MUTED), 530,
           int(fade(t, 1.5, 2.5) * 255))


def scene_problem(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('42 pages. Nobody reads them.', F_BIG, INK), 130,
           int(fade(t, 0.3, 1.2) * 255))
    center(img, text_img('Everyone signs them anyway.', F_BIG, INK), 210,
           int(fade(t, 1.2, 2.0) * 255))
    y0 = 330
    for i in range(8):
        y = y0 + i * 36
        w = 800 * min(max((t - 0.5 - i * 0.15) / 0.6, 0.0), 1.0)
        if w > 0:
            d.rectangle([240, y, 240 + w, y + 14], fill=(70, 72, 80, 255))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in (2, 5):
        a = int(fade(t, 2.4 + i * 0.3, 3.0 + i * 0.3) * 255)
        if a > 0:
            od.rectangle([240, y0 + i * 36, 1040, y0 + i * 36 + 14],
                         fill=RED + (a,))
    img.alpha_composite(ov)
    center(img, text_img('The bad parts hide in there.', F_MED, RED), 640,
           int(fade(t, 4.2, 5.0) * 255))


def scene_what(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('Drop a document.', F_BIG, INK), 150,
           int(fade(t, 0.3, 1.1) * 255))
    center(img, text_img('See the bad parts.', F_BIG, RED), 230,
           int(fade(t, 1.1, 1.9) * 255))
    for i, line in enumerate(('One screen. No samples. Live only.',
                              'Paste text or drop a PDF.')):
        center(img, text_img(line, F_BODY, MUTED), 360 + i * 70,
               int(fade(t, 2.2 + i * 0.8, 3.0 + i * 0.8) * 255))


def scene_demo(img, t, row):
    d = ImageDraw.Draw(img)
    title = row['_title']
    word, color = LAMPWORD[row['lamp']]
    import math
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    if row['lamp'] == 'green':
        # Greens are counts only in the app: no detail card, just a chip.
        d.rounded_rectangle([240, 240, 1040, 430], radius=20,
                            fill=CARD, outline=color + (255,), width=3)
        lamp(img, 330, 335, 42, color, pulse)
        paste(img, text_img(word, F_BIG, color), 410, 285,
              int(fade(t, 0.2, 0.8) * 255))
        paste(img, text_img(title, F_MED, INK), 410, 360,
              int(fade(t, 0.4, 1.0) * 255))
        center(img, text_img('In the app, green parts are counts only. Nothing to open.',
                             F_BODY, MUTED), 480, int(fade(t, 1.2, 1.8) * 255))
        return
    d.rounded_rectangle([110, 70, 1170, 630], radius=20,
                        fill=CARD, outline=color + (255,), width=3)
    lamp(img, 190, 150, 44, color, pulse)
    paste(img, text_img(word, F_BIG, color), 270, 105,
          int(fade(t, 0.2, 0.8) * 255))
    paste(img, text_img(title, F_MED, INK), 270, 180,
          int(fade(t, 0.4, 1.0) * 255))
    y = 250
    for line in wrap(row['plain'] or 'Standard. Nothing to do.', F_BODY, 980):
        paste(img, text_img(line, F_BODY, INK), 150, y,
              int(fade(t, 1.0, 1.8) * 255))
        y += 42
    if row.get('action'):
        y += 20
        d.rounded_rectangle([150, y, 1130, y + 150], radius=12,
                            fill=CARD2, outline=color + (255,), width=2)
        paste(img, text_img('Do this:', F_MED, color), 170, y + 12,
              int(fade(t, 2.0, 2.6) * 255))
        yy = y + 58
        for line in wrap(row['action'], F_BODY, 920)[:2]:
            paste(img, text_img(line, F_BODY, INK), 170, yy,
                  int(fade(t, 2.0, 2.6) * 255))
            yy += 44
    q = 'Quote verified word-for-word.' if row.get('quote_valid') else \
        'Quote not verified. Check this one yourself.'
    paste(img, text_img(q, F_SMALL, MUTED), 150, 655,
          int(fade(t, 2.8, 3.4) * 255))


def scene_how(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('Two readers. One harsh filter.', F_BIG, INK), 90,
           int(fade(t, 0.3, 1.1) * 255))
    boxes = [('STRICT', 'casts a wide net', MUTED),
             ('GENEROUS', 'flags only the genuinely harmful', AMBER),
             ('ADJUDICATOR', 'settles flagged clauses', RED)]
    for i, (name, desc, col) in enumerate(boxes):
        x = 110 + i * 380
        a = int(fade(t, 1.2 + i * 0.9, 2.0 + i * 0.9) * 255)
        if a > 127:
            d.rounded_rectangle([x, 230, x + 340, 400], radius=14,
                                fill=CARD, outline=col + (255,), width=3)
        paste(img, text_img(name, F_MED, col), x + 20, 260, a)
        yy = 320
        for line in wrap(desc, F_SMALL, 300):
            paste(img, text_img(line, F_SMALL, INK), x + 20, yy, a)
            yy += 34
        if i < 2:
            paste(img, text_img('>', F_BIG, MUTED), x + 340, 290, a)
    for i, line in enumerate(('They agree it is bad: red. They disagree: careful.',
                              'Both clear: green. No adjudicator call needed.',
                              'Free tier. $0. No samples, ever.')):
        center(img, text_img(line, F_BODY, INK), 460 + i * 60,
               int(fade(t, 4.2 + i * 0.8, 5.0 + i * 0.8) * 255))


def scene_try(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('Try it on a real document.', F_BIG, INK), 120,
           int(fade(t, 0.3, 1.1) * 255))
    center(img, text_img('github.com/trexgianca777-cmd/lamp', F_MED, INK),
           250, int(fade(t, 1.2, 2.0) * 255))
    center(img, text_img('trexgianca777-cmd.github.io/lamp', F_MED, MUTED),
           330, int(fade(t, 2.0, 2.8) * 255))
    center(img, text_img('Built during the hackathon. Not legal advice.', F_BODY, MUTED),
           470, int(fade(t, 3.0, 3.8) * 255))
    d.line([240, 600, 1040, 600], fill=(70, 72, 80, 255), width=2)
    sx = 240 + int((t * 160) % 800)
    lamp(img, sx, 600, 26, RED, 0.5)


def main():
    demo = json.load(open('/tmp/video-demo.json'))
    assert len(demo) >= 4, f'demo rows: {len(demo)}'
    for r in demo:
        r['_title'] = r['title']

    scenes = [(0, 12, lambda im, t: scene_title(im, t)),
              (12, 30, lambda im, t: scene_problem(im, t - 12)),
              (30, 52, lambda im, t: scene_what(im, t - 30))]
    t = 52
    for r in demo:
        scenes.append((t, t + 14, (lambda row: (lambda im, tt: scene_demo(im, tt, row)))(r)))
        t += 14
    scenes.append((t, t + 26, lambda im, tt: scene_how(im, tt)))
    t += 26
    scenes.append((t, t + 17, lambda im, tt: scene_try(im, tt)))
    total = t + 17
    print(f'total seconds: {total}, demo lamps: {[r["lamp"] for r in demo]}', flush=True)

    cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20',
           '/tmp/legal-lights-demo2.mp4']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    for f in range(nframes):
        tt = f / FPS
        img = bg_image()
        for s0, s1, fn in scenes:
            if s0 <= tt < s1:
                fn(img, tt - s0)
                break
        proc.stdin.write(img.convert('RGB').tobytes())
        if f % (FPS * 15) == 0:
            print(f'frame {f}/{nframes} ({tt:.0f}s)', flush=True)
    proc.stdin.close()
    proc.wait()
    print('wrote /tmp/legal-lights-demo2.mp4')


if __name__ == '__main__':
    main()
