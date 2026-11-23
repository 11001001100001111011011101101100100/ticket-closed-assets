"""
Ticket Closed: IT Memes - meme + Reel builder (Pillow + ffmpeg, no installs).

Meme: 1080x1080 two-box "X vs. Y" card. Reel: 1080x1920, ~11 s, same card, then the green-check end card.
Matches the existing it_meme_*.png / ticket_closed_reel_*.mp4 look (navy background, blue top box, orange or green bottom box).

build_meme(m, out_png)        m = dict(header, l1, t1, l2, t2, c2, q)
build_reel(m, out_mp4, tmpdir)
"""
import os, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

NAVY, BOX, BLUE = (0, 25, 74), (0, 18, 55), (0, 94, 255)
ORANGE, GREEN, MUTED, WHITE = (255, 131, 49), (3, 194, 82), (179, 189, 208), (255, 255, 255)
_FD = "/usr/share/fonts/truetype/liberation/"


def F(sz, bold=True):
    return ImageFont.truetype(_FD + ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"), sz)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _box(d, rect, color, label, text, label_sz, text_sz, line_h, text_dy, max_lines, pad=40, label_dy=22):
    x0, y0, x1, y1 = rect
    d.rounded_rectangle(rect, 28, fill=BOX, outline=color, width=4)
    d.text((x0 + pad, y0 + label_dy), label, font=F(label_sz), fill=color)
    sz = text_sz
    while True:
        f = F(sz)
        lines = wrap(d, text, f, (x1 - x0) - 2 * pad)
        if len(lines) <= max_lines or sz <= 36:
            break
        sz -= 2
    yy = y0 + text_dy
    for ln in lines:
        d.text((x0 + pad, yy), ln, font=f, fill=WHITE)
        yy += int(sz * line_h)


def build_meme(m, out):
    W = H = 1080
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 62), m["header"], font=F(40), fill=MUTED, anchor="mm")
    _box(d, (60, 110, 1020, 510), BLUE, m["l1"], m["t1"], 40, 54, 1.22, 96, 4, label_dy=28)
    d.text((W // 2, 545), "vs.", font=F(48), fill=MUTED, anchor="mm")
    _box(d, (60, 580, 1020, 980), GREEN if m.get("c2") == "green" else ORANGE, m["l2"], m["t2"], 40, 54, 1.22, 96, 4, label_dy=28)
    d.text((W // 2, 1030), "TICKET CLOSED: IT MEMES", font=F(34, False), fill=MUTED, anchor="mm")
    img.save(out)
    return out


def _reel_frame(m, mode, out):
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    if mode in ("A", "B"):
        d.text((W // 2, 200), m["header"], font=F(44), fill=MUTED, anchor="mm")
        if mode == "A":
            _box(d, (70, 380, 1010, 960), BLUE, m["l1"], m["t1"], 50, 66, 1.22, 140, 4, pad=45, label_dy=32)
        else:
            _box(d, (70, 260, 1010, 840), BLUE, m["l1"], m["t1"], 50, 66, 1.22, 140, 4, pad=45, label_dy=32)
            d.text((W // 2, 903), "vs.", font=F(56), fill=MUTED, anchor="mm")
            _box(d, (70, 980, 1010, 1560), GREEN if m.get("c2") == "green" else ORANGE, m["l2"], m["t2"], 50, 66, 1.22, 140, 4, pad=45, label_dy=32)
    else:
        cx, cy, r = 540, 520, 190
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN)
        d.line([(442, 540), (515, 603)], fill=WHITE, width=44)
        d.line([(515, 603), (648, 442)], fill=WHITE, width=44)
        for p in [(442, 540), (515, 603), (648, 442)]:
            d.ellipse((p[0] - 22, p[1] - 22, p[0] + 22, p[1] + 22), fill=WHITE)
        qf = F(70)
        lines = wrap(d, m["q"], qf, 900)
        y = 860
        for ln in lines:
            d.text((W // 2, y), ln, font=qf, fill=WHITE, anchor="mm")
            y += 82
        d.text((W // 2, y + 22), "Tell us in the comments", font=F(46, False), fill=MUTED, anchor="mm")
        d.rounded_rectangle((130, 1420, 950, 1550), 65, fill=BLUE)
        d.text((540, 1485), "FOLLOW FOR DAILY IT MEMES", font=F(42), fill=WHITE, anchor="mm")
    d.text((W // 2, 1750), "TICKET CLOSED: IT MEMES", font=F(40), fill=MUTED, anchor="mm")
    img.save(out)


def build_reel(m, out, tmp):
    os.makedirs(tmp, exist_ok=True)
    for mode in "ABC":
        _reel_frame(m, mode, os.path.join(tmp, mode + ".png"))
    cmd = ["ffmpeg", "-v", "error", "-y",
           "-loop", "1", "-t", "3.5", "-i", os.path.join(tmp, "A.png"),
           "-loop", "1", "-t", "4.5", "-i", os.path.join(tmp, "B.png"),
           "-loop", "1", "-t", "4.0", "-i", os.path.join(tmp, "C.png"),
           "-filter_complex",
           "[0][1]xfade=transition=fade:duration=0.5:offset=3.0[v1];[v1][2]xfade=transition=fade:duration=0.5:offset=7.0,format=yuv420p[v]",
           "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


if __name__ == "__main__":
    t = dict(header="IT SUPPORT: FILE MANAGEMENT", l1="THE USER", t1='"I just save everything on the desktop."',
             l2="IT", t2="I would rather you didn't. But here we are.", c2="orange", q="Where do you actually save your files?")
    build_meme(t, "test_meme.png")
    build_reel(t, "test_reel.mp4", "tmp_reel")
