"""
Ticket Closed: Fix of the Day - card builder (Pillow only).
Needs in the same folder: david_character.png (full-size original, white background).
Output is 1080x1350 (4:5) for Facebook and Instagram, same banner/colors as the Daily News cards.
"""
import re
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

W, H = 1080, 1350
NAVY, GREEN, BLUE, RED = (0, 25, 74), (3, 194, 82), (0, 94, 255), (214, 32, 39)
MUTED, OL = (179, 189, 208), (30, 30, 30)
# VS Code Dark+ (Chat theme code view)
C_BG, C_TXT = (30, 30, 30), (212, 212, 212)
C_COMMENT, C_STR, C_KEY, C_FUNC, C_VAR = (106, 153, 85), (206, 145, 120), (86, 156, 214), (220, 220, 170), (156, 220, 254)
_FD = "/usr/share/fonts/truetype/liberation/"
_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def F(sz, bold=True):
    return ImageFont.truetype(_FD + ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"), sz)


def cut_white_bg(im, tol=14):
    """Near-white studio background -> transparent (flood fill from top/upper sides so white clothing is kept)."""
    im = im.convert("RGB")
    w, h = im.size
    mark = (255, 0, 255)
    seeds = [(x, 2) for x in range(2, w - 2, 48)]
    for y in range(2, int(h * 0.45), 48):
        seeds += [(2, y), (w - 3, y)]
    for sd in seeds:
        px = im.getpixel(sd)
        if min(px) >= 236 and px != mark:
            ImageDraw.floodfill(im, sd, mark, thresh=tol)
    r, g, b = im.split()
    m = ImageChops.darker(ImageChops.darker(r.point(lambda v: 255 if v == 255 else 0),
                                            g.point(lambda v: 255 if v == 0 else 0)),
                          b.point(lambda v: 255 if v == 255 else 0))
    alpha = ImageChops.invert(m).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


_PORTRAIT = {}


def prep_portrait(path):
    if path not in _PORTRAIT:
        cut = cut_white_bg(Image.open(path).convert("RGB"))
        _PORTRAIT[path] = cut.crop((0, 0, cut.width, int(cut.height * 0.76)))
    return _PORTRAIT[path]


def tokenize(line):
    """Tiny PowerShell highlighter -> [(text, color)]."""
    out = []
    for m in re.finditer(r'(#.*$)|("[^"]*")|(\b[A-Z][a-z]+-[A-Za-z]+\b)|(-[A-Za-z]+\b)|(\$\w+:?\w*)|(\s+)|([^\s"]+)', line):
        t = m.group(0)
        if m.group(1):
            c = C_COMMENT
        elif m.group(2):
            c = C_STR
        elif m.group(3):
            c = C_FUNC
        elif m.group(4):
            c = C_KEY
        elif m.group(5):
            c = C_VAR
        else:
            c = C_TXT
        out.append((t, c))
    return out


def build_fix_card(problem, sub, david_line, code, warning, why="", tag="Resolution: fixed",
                   david_path="david_character.png", out="fix_card.png"):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    def wrap(text, font, maxw):
        words, lines, cur = text.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font) <= maxw:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        return lines

    # ---- banner: TICKET CLOSED: (white) FIX OF THE DAY (green)
    d.rectangle([0, 0, W, 110], fill=NAVY)
    f = F(56)
    d.text((40, 24), "TICKET CLOSED:", font=f, fill="white")
    d.text((40 + d.textlength("TICKET CLOSED:", font=f) + 16, 24), "FIX OF THE DAY", font=f, fill=GREEN)
    d.rectangle([0, 110, 330, 168], fill=BLUE)
    d.text((22, 118), "TODAY'S FIX", font=F(36), fill="white")

    # ---- problem headline
    y, hf = 188, F(54)
    for ln in wrap(problem, hf, W - 80):
        d.text((40, y), ln, font=hf, fill=(15, 15, 15))
        y += 62
    d.text((40, y + 6), sub, font=F(26, False), fill=(70, 70, 70))
    scene_top = y + 62

    # ---- measure the lower blocks first so the scene fills the leftover space exactly
    code_w = W - 80 - 48
    msz = 25
    while msz > 20 and max(ImageFont.truetype(_MONO, msz).getlength(l) for l in code) > code_w:
        msz -= 1
    clh = int(msz * 1.75)
    ch_est = 28 + clh * len(code) + 14
    wf_ = F(27, False)
    why_lines = min(2, len(wrap("Why it works: " + why, wf_, W - 80))) if why else 0
    why_h = (20 + 36 * why_lines) if why else 0
    wlab = F(28)
    wtxt = F(26, False)
    w_avail = (W - 80) - 24 - int(d.textlength("HEADS UP", font=wlab)) - 20 - 24
    warn_lines = wrap(warning, wtxt, w_avail)[:2]
    warn_h = 78 if len(warn_lines) == 1 else 112
    scene_h = 1244 - scene_top - 24 - ch_est - 22 - warn_h - why_h
    scene_h = max(380, min(640, scene_h))

    # ---- scene: David gives the fix
    sc = (40, scene_top, W - 40, scene_top + scene_h)
    d.rounded_rectangle(sc, 24, fill=(228, 238, 255), outline=NAVY, width=4)
    d.rectangle([sc[0] + 4, sc[3] - 70, sc[2] - 4, sc[3] - 4], fill=(196, 208, 232))
    crop = prep_portrait(david_path)
    th = scene_h - 20
    tw = int(crop.width * th / crop.height)
    dav = crop.resize((tw, th), Image.LANCZOS)
    dx, dy = sc[2] - 6 - tw, sc[3] - th - 5
    img.paste(dav, (dx, dy), dav)
    d = ImageDraw.Draw(img)

    bx = (66, scene_top + 24, dx + 40, scene_top + min(300, scene_h - 110))
    x0, y0, x1, y1 = bx
    d.rounded_rectangle(bx, 30, fill=(255, 250, 225), outline=OL, width=5)
    d.polygon([(x1 - 150, y1 - 3), (x1 - 50, y1 - 3), (x1 + 30, y1 + 50)], fill=(255, 250, 225), outline=OL)
    d.line([(x1 - 147, y1 - 2), (x1 - 53, y1 - 2)], fill=(255, 250, 225), width=8)
    bf = F(34)
    lines = wrap(david_line, bf, (x1 - x0) - 44)
    lh = bf.size + 8
    yy = y0 + ((y1 - y0) - lh * len(lines)) / 2
    for ln in lines:
        d.text(((x0 + x1) / 2, yy), ln, font=bf, fill=(10, 10, 10), anchor="ma")
        yy += lh
    d.rounded_rectangle(sc, 24, outline=NAVY, width=4)

    # ---- code panel (VS Code Dark+)
    cy0 = sc[3] + 24
    mf = ImageFont.truetype(_MONO, msz)
    lh = clh
    ch = 28 + lh * len(code) + 14
    d.rounded_rectangle((40, cy0, W - 40, cy0 + ch), 18, fill=C_BG, outline=(38, 60, 101), width=3)
    d.ellipse((62, cy0 + 12, 74, cy0 + 24), fill=(255, 95, 86))
    d.ellipse((84, cy0 + 12, 96, cy0 + 24), fill=(255, 189, 46))
    d.ellipse((106, cy0 + 12, 118, cy0 + 24), fill=(39, 201, 63))
    yy = cy0 + 34
    for ln in code:
        xx = 64
        for t, c in tokenize(ln):
            d.text((xx, yy), t, font=mf, fill=c)
            xx += d.textlength(t, font=mf)
        yy += lh
    cb = cy0 + ch

    # ---- caution strip
    wy = cb + 22
    d.rounded_rectangle((40, wy, W - 40, wy + warn_h), 16, fill=(255, 241, 224), outline=(255, 131, 49), width=3)
    lab_w = d.textlength("HEADS UP", font=wlab)
    ty = wy + (warn_h - (34 * len(warn_lines))) // 2 - 2
    d.text((64, ty + 2), "HEADS UP", font=wlab, fill=(200, 90, 10))
    for i, ln in enumerate(warn_lines):
        d.text((64 + lab_w + 20, ty + 4 + 34 * i), ln, font=wtxt, fill=(60, 40, 20))

    # ---- why it works
    if why:
        wf = F(27, False)
        yy = wy + warn_h + 20
        lead = "Why it works: "
        d.text((40, yy), lead, font=F(27), fill=NAVY)
        first = True
        for ln in wrap(lead + why, wf, W - 80)[:2]:
            if first:
                ln = ln[len(lead):] if ln.startswith(lead) else ln
                d.text((40 + d.textlength(lead, font=F(27)), yy), ln, font=wf, fill=(50, 50, 50))
                first = False
            else:
                d.text((40, yy), ln, font=wf, fill=(50, 50, 50))
            yy += 36

    # ---- footer
    d.rectangle([0, 1268, W, H], fill=NAVY)
    d.text((40, 1285), "TICKET CLOSED:", font=F(34), fill="white")
    d.text((40 + d.textlength("TICKET CLOSED:", font=F(34)) + 10, 1285), "FIX OF THE DAY", font=F(34), fill=GREEN)
    d.text((W - 40, 1292), tag, font=F(26, False), fill=MUTED, anchor="ra")
    img.save(out)
    return out, wy + warn_h + why_h
