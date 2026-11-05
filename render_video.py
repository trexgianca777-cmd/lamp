#!/usr/bin/env python3
"""Render the Legal Lights demo video: animated frames piped to ffmpeg.

165 seconds, 1280x720, 24fps. All demo data comes from a real live run
(/tmp/demo-panel.json) on real clauses from a real lease. No samples,
no mocked lamps: lamp colors, plain lines, and actions are the model's
own outputs. Captions are burned in; narration is muxed separately
if an audio track exists.
"""
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 24
BG = (13, 15, 18)
INK = (242, 240, 234)
MUTED = (150, 150, 150)
RED = (229, 72, 77)
AMBER = (245, 166, 35)
GREEN = (70, 167, 88)
WHITE = (216, 216, 216)
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
    for k, a in ((2.2, 40), (1.6, 80)):
        rr = r * k * (0.9 + 0.1 * pulse)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (a,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,))


def fade(t, t0, t1):
    if t < t0:
        return 0.0
    if t > t1:
        return 1.0
    return (t - t0) / (t1 - t0)


def slide(t, t0, dist=60):
    # 0..1 progress of a slide-in over 0.8s starting at t0
    p = min(max((t - t0) / 0.8, 0.0), 1.0)
    return dist * (1 - p)


# ---------------- scenes ----------------

def scene_title(img, t):
    d = ImageDraw.Draw(img)
    a = fade(t, 0.3, 1.3)
    center(img, text_img('LEGAL LIGHTS', F_TITLE, INK), 220 - slide(t, 0.3), int(a * 255))
    import math
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    for i, c in enumerate((RED, AMBER, GREEN)):
        lamp(img, 490 + i * 150, 420, 42, c, pulse if i == int(t * 1.5) % 3 else 0.2)
    center(img, text_img('Fine print, lit up.', F_MED, MUTED), 520, int(fade(t, 1.5, 2.5) * 255))


def scene_problem(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('42 pages. Nobody reads them.', F_BIG, INK), 130, int(fade(t, 0.3, 1.2) * 255))
    center(img, text_img('Everyone signs them anyway.', F_BIG, INK), 210, int(fade(t, 1.2, 2.0) * 255))
    # document lines with red highlights sweeping in
    y0 = 330
    for i in range(8):
        y = y0 + i * 36
        d.rectangle([240, y, 1040, y + 14], fill=(60, 60, 66, 255))
    sweep = min(max((t - 2.2) / 2.5, 0.0), 1.0)
    n = int(sweep * 8)
    for i in range(n):
        y = y0 + i * 36
        d.rectangle([240, y, 1040, y + 14], fill=RED + (255,))
    if sweep >= 1.0:
        center(img, text_img('The bad parts hide in there.', F_MED, RED), 640, int(fade(t, 5.0, 5.8) * 255))


def scene_what(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('Drop a document.', F_BIG, INK), 150, int(fade(t, 0.3, 1.1) * 255))
    center(img, text_img('See the bad parts.', F_BIG, RED), 230, int(fade(t, 1.1, 1.9) * 255))
    for i, line in enumerate(('One screen. No samples. Live only.',
                              'Paste text or drop a PDF.',
                              'Every lamp traces to quoted wording.')):
        center(img, text_img(line, F_BODY, MUTED), 360 + i * 70, int(fade(t, 2.2 + i * 0.8, 3.0 + i * 0.8) * 255))


def scene_demo(img, t, row):
    d = ImageDraw.Draw(img)
    title = row['_title']
    word, color = LAMPWORD[row['lamp']]
    import math
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    lamp(img, 150, 130, 46, color, pulse)
    paste(img, text_img(word, F_BIG, color), 280, 88, int(fade(t, 0.2, 0.8) * 255))
    paste(img, text_img(title, F_MED, INK), 280, 165, int(fade(t, 0.4, 1.0) * 255))
    y = 260
    for line in wrap(row['plain'] or 'Standard. Nothing to do.', F_BODY, 1000):
        paste(img, text_img(line, F_BODY, INK), 110, y, int(fade(t, 1.0, 1.8) * 255))
        y += 46
    if row.get('action'):
        y += 20
        d.rectangle([110, y, 1170, y + 162], outline=color + (255,), width=3)
        paste(img, text_img('Do this:', F_MED, color), 130, y + 12, int(fade(t, 2.0, 2.6) * 255))
        yy = y + 58
        for line in wrap(row['action'], F_BODY, 980)[:2]:
            paste(img, text_img(line, F_BODY, INK), 130, yy, int(fade(t, 2.0, 2.6) * 255))
            yy += 44
    q = 'Quote verified word-for-word.' if row.get('quote_valid') else \
        'Quote not verified. Check this one yourself.'
    paste(img, text_img(q, F_SMALL, MUTED), 110, 640, int(fade(t, 2.8, 3.4) * 255))


def scene_how(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('Two readers. One harsh filter.', F_BIG, INK), 90, int(fade(t, 0.3, 1.1) * 255))
    boxes = [('STRICT', 'casts a wide net', MUTED),
             ('GENEROUS', 'flags only the genuinely harmful', AMBER),
             ('ADJUDICATOR', 'settles flagged clauses', RED)]
    for i, (name, desc, col) in enumerate(boxes):
        x = 110 + i * 380
        a = int(fade(t, 1.2 + i * 0.9, 2.0 + i * 0.9) * 255)
        d.rectangle([x, 230, x + 340, 400], outline=col + (a,), width=3)
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
        center(img, text_img(line, F_BODY, INK), 460 + i * 60, int(fade(t, 4.2 + i * 0.8, 5.0 + i * 0.8) * 255))


def scene_try(img, t):
    d = ImageDraw.Draw(img)
    center(img, text_img('Try it on a real document.', F_BIG, INK), 120, int(fade(t, 0.3, 1.1) * 255))
    center(img, text_img('github.com/trexgianca777-cmd/legal-lights', F_MED, INK), 250, int(fade(t, 1.2, 2.0) * 255))
    center(img, text_img('trexgianca777-cmd.github.io/legal-lights', F_MED, MUTED), 330, int(fade(t, 2.0, 2.8) * 255))
    center(img, text_img('Built during the hackathon. Not legal advice.', F_BODY, MUTED), 470, int(fade(t, 3.0, 3.8) * 255))
    import math
    pulse = 0.5 + 0.5 * math.sin(t * 4)
    for i, c in enumerate((RED, AMBER, GREEN)):
        lamp(img, 490 + i * 150, 600, 30, c, pulse if i == int(t * 1.5) % 3 else 0.2)


def main():
    # Demo data is an explicit list written by the build step, either
    # from a fresh live run or from already-verified panel rows:
    # [{"title","lamp","plain","action","quote_valid"}]. Nothing here
    # is mocked: every row is a real model verdict on a real clause.
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
           '/tmp/legal-lights-demo.mp4']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    for f in range(nframes):
        tt = f / FPS
        img = Image.new('RGBA', (W, H), BG + (255,))
        for s0, s1, fn in scenes:
            if s0 <= tt < s1:
                fn(img, tt - s0)
                break
        proc.stdin.write(img.convert('RGB').tobytes())
        if f % (FPS * 15) == 0:
            print(f'frame {f}/{nframes} ({tt:.0f}s)', flush=True)
    proc.stdin.close()
    proc.wait()
    print('wrote /tmp/legal-lights-demo.mp4')


if __name__ == '__main__':
    main()
