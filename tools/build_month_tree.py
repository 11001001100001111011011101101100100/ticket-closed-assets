"""
Build the Ticket Closed content tree inside the assets repo.

  <repo>/<year>/<MM-Month>/{daily-news,daily-meme,daily-fix,daily-reel}/  + schedule.csv per month

Stages are cached (existing outputs are skipped), so re-running resumes.
Usage: python3 build_month_tree.py <repo_root> [--src /tmp/claude-tool-results] [--stage tree|existing|new|csv|all]
"""
import os, re, sys, csv, glob, shutil, datetime, calendar, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image
from meme_data import MEMES, fb_caption
from fix_data import FIXES, caption as fix_caption
from fix_data_new import FIXES_NEW
from fix_card import build_fix_card
from meme_factory import build_meme, build_reel

OWNER_REPO = "11001001100001111011011101101100100/ticket-closed-assets"
RAW = f"https://raw.githubusercontent.com/{OWNER_REPO}/main/"
SUBS = ["daily-news", "daily-meme", "daily-fix", "daily-reel"]
D = datetime.date
ALL_FIXES = FIXES + FIXES_NEW

NEWS_TXT = {
"2026-11-22": """TICKET CLOSED: DAILY NEWS - 2026-11-22 (satire card)
HEADLINE: WINDOWS UPDATE FINALLY ACHIEVES ZERO-RESTART COMPUTING: APPS NO LONGER START EITHER
CAST: Brenda (customer), David (IT), Dr. Pat Reboot (fake expert quote)
SOURCE: https://www.neowin.net/news/microsoft-confirms-november-2026-windows-11-hotpatch-breaks-app-installs-and-launches/ (Neowin, Nov 19 2026: Microsoft confirms hotpatch KB5132043 can cause 0xC0000099 errors installing/opening apps that use 32-bit msi.dll; temporary registry workaround HotPatchTableSize=2000)
IMAGE: card image not stored here (posted manually from phone)

FACEBOOK CAPTION:
Microsoft says this month's Windows 11 hotpatch (KB5132043) can break app installs and launches with error 0xC0000099. The update promised no restart. It did not promise the apps would start. The temporary fix is a registry edit, so bring coffee and a backup. Ticket closed. (Resolution: regedit.)
#ITHumor #HelpDesk #Windows11 #SysAdmin #TicketClosed

INSTAGRAM CAPTION:
Microsoft says this month's Windows 11 hotpatch (KB5132043) can break app installs and launches with error 0xC0000099. The update promised no restart. It did not promise the apps would start. The temporary fix is a registry edit, so bring coffee and a backup. Ticket closed. (Resolution: regedit.)
#ITHumor #HelpDesk #Windows11 #SysAdmin #ITSupport #TechHumor #Microsoft #PatchTuesday #ITLife #DesktopSupport #TicketClosed #SysadminLife

POST STATUS: POSTED MANUALLY to Facebook and Instagram by David on 2026-11-22.
""",
"2026-11-23": """DATE: 2026-11-23
FORMAT: TICKET CLOSED: DAILY NEWS satire card (Chad / David / Dr. Pat Reboot)
HEADLINE: UPDATE THAT NEEDS NO RESTART ALSO NEEDS NO PRINTING: OFFICE GOES PAPERLESS AGAINST ITS WILL
SOURCE: https://windowsreport.com/microsoft-confirms-windows-11-kb5132043-hotpatch-breaks-printing-for-forcepoint-users/ (Microsoft service alert WI1562175; hotpatch KB5132043 + Forcepoint DLP Endpoint Agent on Windows 11 24H2+: Print greyed out, Print Spooler won't start; workaround exists, no permanent fix)
IMAGE: card image not stored here

FB CAPTION:
Satire from Ticket Closed: Daily News. Microsoft confirms hotpatch KB5132043 can leave Windows 11 PCs running Forcepoint DLP with a greyed-out Print button. The update said no restart. It said nothing about printing. Resolution: patched into paperless. Ticket closed.
#ITHumor #HelpDesk #Windows11 #SysAdmin #TicketClosed

IG CAPTION:
Satire from Ticket Closed: Daily News. Microsoft confirms hotpatch KB5132043 can leave Windows 11 PCs running Forcepoint DLP with a greyed-out Print button. The update said no restart. It said nothing about printing. Resolution: patched into paperless. Ticket closed.
#ITHumor #HelpDesk #Windows11 #SysAdmin #ITSupport #TechHumor #Microsoft #Hotpatch #PrintSpooler #ITLife #DesktopSupport #TicketClosed

POST STATUS: Facebook post verified published on 2026-11-23. Instagram: confirm.
""",
}


def month_dir(root, d):
    return os.path.join(root, str(d.year), f"{d.month:02d}-{calendar.month_name[d.month]}")


def rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += datetime.timedelta(days=1)


def find_src(src, name, ext):
    pat = re.compile(r"^project-file-[0-9a-f-]{36}-(.+)-[0-9a-f]{8}\." + ext + "$")
    for p in sorted(glob.glob(os.path.join(src, "*", "project-file-*." + ext))):
        m = pat.match(os.path.basename(p))
        if m and m.group(1) == name:
            return p
    raise FileNotFoundError(name)


def meme_name(n):
    return {2: "it_meme_2_event_log", 3: "it_meme_3_remote", 4: "it_meme_4_wifi", 5: "it_meme_5_update", 6: "it_meme_6_password"}.get(n, f"it_meme_{n}")


def jpg_from_png(png, jpg):
    Image.open(png).convert("RGB").save(jpg, quality=92)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_existing_csv(src_csv):
    rows = list(csv.reader(open(src_csv, encoding="utf-8-sig")))[1:]
    out = {}
    for r in rows:
        iso = r[0]
        kind = "meme" if r[2] == "Photo meme" else "reel"
        out[(iso, kind)] = dict(title=r[4], caption=r[5])
    return out


def run(root, src, stage):
    root = os.path.abspath(root)
    first, last = D(2026, 11, 19), D(2027, 12, 31)
    # ---------- tree
    if stage in ("tree", "all"):
        y, m = 2026, 11
        while (y, m) <= (2027, 12):
            base = month_dir(root, D(y, m, 1))
            for s in SUBS:
                p = os.path.join(base, s)
                os.makedirs(p, exist_ok=True)
                open(os.path.join(p, ".gitkeep"), "a").close()
            m += 1
            if m == 13:
                y, m = y + 1, 1
        print("tree ok")
    # ---------- existing assets (Nov 19 - Dec 19 memes/reels, Nov 22 - Dec 21 fixes, news txt)
    existing = load_existing_csv(glob.glob(os.path.join(src, "*", "project-file-*-schedule-*.csv"))[0])
    if stage in ("existing", "all"):
        n = 1
        for d in daterange(D(2026, 11, 19), D(2026, 12, 19)):
            iso = d.isoformat()
            mdir = month_dir(root, d)
            # meme (Nov 19 = it_support_meme.png, assumed meme #1; others it_meme_N)
            mname = "it_support_meme" if d == D(2026, 11, 19) else meme_name(n)
            png = os.path.join(mdir, "daily-meme", f"{iso}_meme.png")
            jpg = png[:-4] + ".jpg"
            if not os.path.exists(png):
                shutil.copy(find_src(src, mname, "png"), png)
            if not os.path.exists(jpg):
                jpg_from_png(png, jpg)
            reel = os.path.join(mdir, "daily-reel", f"{iso}_reel.mp4")
            if not os.path.exists(reel):
                shutil.copy(find_src(src, f"ticket_closed_reel_{n}", "mp4"), reel)
            cap_m = existing.get((iso, "meme"), {}).get("caption")
            cap_r = existing.get((iso, "reel"), {}).get("caption")
            title = existing.get((iso, "reel"), {}).get("title", "")
            note = "" if cap_m else "Posted Nov 19. Original caption is not stored in the project.\n"
            wd = d.strftime("%A")
            write(os.path.join(mdir, "daily-meme", f"{iso}_meme.txt"),
                  f"TICKET CLOSED: IT MEMES - PHOTO MEME - {iso} ({wd})\nPOST TIME: 12:00 PM ET\nIMAGE: {iso}_meme.jpg (1080x1080), PNG master {iso}_meme.png\n"
                  f"SOURCE FILE: {mname}.png\n{note}\nCAPTION (Facebook and Instagram):\n{cap_m or '(not stored)'}\n")
            write(os.path.join(mdir, "daily-reel", f"{iso}_reel.txt"),
                  f"TICKET CLOSED: IT MEMES - REEL - {iso} ({wd})\nPOST TIME: 8:00 PM ET\nVIDEO: {iso}_reel.mp4 (1080x1920)\nSOURCE FILE: ticket_closed_reel_{n}.mp4\nTITLE: {title or '(not stored)'}\n\nCAPTION (Facebook and Instagram):\n{cap_r or '(not stored)'}\n")
            n += 1
        for iso, text in NEWS_TXT.items():
            write(os.path.join(month_dir(root, D.fromisoformat(iso)), "daily-news", f"{iso}_news.txt"), text)
        print("existing memes/reels/news ok")
    # ---------- fix cards (all 71) + new memes/reels
    if stage in ("new", "all"):
        david = os.path.join(HERE, "david_character.png")
        for f in ALL_FIXES:
            d = D.fromisoformat(f["date"])
            iso = f["date"]
            fdir = os.path.join(month_dir(root, d), "daily-fix")
            jpg = os.path.join(fdir, f"{iso}_fix.jpg")
            if not os.path.exists(jpg):
                tmp = os.path.join("/tmp", f"fix_{iso}.png")
                build_fix_card(f["problem"], f["sub"], f["david"], f["code"], f["warn"], f["why"], "Resolution: " + f["res"], david_path=david, out=tmp)
                jpg_from_png(tmp, jpg)
                os.remove(tmp)
            tested = "command logic reviewed, not run on a live endpoint"
            write(os.path.join(fdir, f"{iso}_fix.txt"),
                  f"TICKET CLOSED: FIX OF THE DAY - {iso} ({d.strftime('%A')})\nPOST TIME: 2:00 PM ET\nTITLE: {f['problem']}\nHOST: David (IT)\nIMAGE: {iso}_fix.jpg (1080x1350)\n"
                  f"TESTED: {tested}.\n\nFACEBOOK CAPTION:\n{fix_caption(f)}\n\nINSTAGRAM CAPTION:\n{fix_caption(f, True)}\n")
        print("fix cards ok", len(ALL_FIXES))
        for i, m in enumerate(MEMES):
            d = D.fromisoformat(m["date"])
            iso = m["date"]
            mdir = month_dir(root, d)
            png = os.path.join(mdir, "daily-meme", f"{iso}_meme.png")
            jpg = png[:-4] + ".jpg"
            if not os.path.exists(png):
                build_meme(m, png)
            if not os.path.exists(jpg):
                jpg_from_png(png, jpg)
            cap = fb_caption(m, i)
            wd = d.strftime("%A")
            write(os.path.join(mdir, "daily-meme", f"{iso}_meme.txt"),
                  f"TICKET CLOSED: IT MEMES - PHOTO MEME - {iso} ({wd})\nPOST TIME: 12:00 PM ET\nIMAGE: {iso}_meme.jpg (1080x1080), PNG master {iso}_meme.png\n\nCAPTION (Facebook and Instagram):\n{cap}\n")
            reel = os.path.join(mdir, "daily-reel", f"{iso}_reel.mp4")
            if not os.path.exists(reel):
                build_reel(m, reel, os.path.join("/tmp", f"reel_tmp_{iso}"))
            write(os.path.join(mdir, "daily-reel", f"{iso}_reel.txt"),
                  f"TICKET CLOSED: IT MEMES - REEL - {iso} ({wd})\nPOST TIME: 8:00 PM ET\nVIDEO: {iso}_reel.mp4 (1080x1920, about 11 s, silent)\nTITLE: {m['title']}\n\nCAPTION (Facebook and Instagram):\n{cap}\n")
        print("new memes/reels ok", len(MEMES))
    # ---------- schedule.csv per month
    if stage in ("csv", "all"):
        y, m = 2026, 11
        while (y, m) <= (2027, 12):
            first_day = D(y, m, 1)
            base = month_dir(root, first_day)
            ndays = calendar.monthrange(y, m)[1]
            rows = []
            for day in range(1, ndays + 1):
                d = D(y, m, day)
                if d < D(2026, 11, 19):
                    continue
                iso = d.isoformat()
                wd = d.strftime("%a")
                slots = [("6:00 AM", "Daily News", "daily-news", "news", ".jpg"),
                         ("12:00 PM", "Photo meme", "daily-meme", "meme", ".jpg"),
                         ("2:00 PM", "Fix of the Day", "daily-fix", "fix", ".jpg"),
                         ("8:00 PM", "Reel", "daily-reel", "reel", ".mp4")]
                for t, slot, sub, kind, ext in slots:
                    path = os.path.join(base, sub, f"{iso}_{kind}{ext}")
                    txt = os.path.join(base, sub, f"{iso}_{kind}.txt")
                    exists = os.path.exists(path)
                    fbcap = igcap = ""
                    if os.path.exists(txt):
                        body = open(txt, encoding="utf-8").read()
                        if kind in ("meme", "reel"):
                            fbcap = igcap = body.split("CAPTION (Facebook and Instagram):\n", 1)[-1].strip() if "CAPTION (Facebook" in body else ""
                        else:
                            mfb = re.search(r"(?:FACEBOOK CAPTION|FB CAPTION):\n(.*?)\n\n(?:INSTAGRAM|IG) CAPTION:\n(.*?)(?:\n\n[A-Z ]+:|\Z)", body, re.S)
                            if mfb:
                                fbcap, igcap = mfb.group(1).strip(), mfb.group(2).strip()
                    # status
                    if kind == "news":
                        if iso == "2026-11-22":
                            fbs, igs, note = "Posted (manual)", "Posted (manual)", ""
                        elif iso == "2026-11-23":
                            fbs, igs, note = "Posted (verified)", "Confirm", ""
                        else:
                            fbs = igs = "To make and post that morning"
                            note = "Built from the day's real IT news"
                    elif kind == "meme":
                        fbs = igs = "Scheduled/posted (per David)" if d <= D(2026, 12, 19) else "To schedule"
                        note = "Nov 19 file assumed to be meme #1" if iso == "2026-11-19" else ""
                    elif kind == "fix":
                        fbs = igs = "Scheduled/posted (per David)" if d <= D(2026, 12, 21) else "To schedule"
                        note = ""
                    else:
                        if d <= D(2026, 12, 19):
                            fbs, igs = "Scheduled/posted (per David)", "Manual (per David)"
                        else:
                            fbs, igs = "To schedule (Business Suite)", "To post (Windsor create_video_post, immediate)"
                        note = ""
                    if not exists:
                        if kind == "news":
                            fname, url = "(made that morning)", ""
                        else:
                            fname, url = "(not made yet)", ""
                            fbs = igs = "Not made"
                            note = ""
                        if kind == "news" and iso in NEWS_TXT:
                            fname, url = "(card image not stored)", ""
                    else:
                        fname = rel(path, root)
                        url = RAW + fname
                    if kind == "news" and os.path.exists(txt) and not exists:
                        fname = rel(txt, root)
                        url = RAW + fname
                    rows.append([iso, wd, t, slot, fname, url, fbcap, igcap, fbs, igs, note])
            with open(os.path.join(base, "schedule.csv"), "w", encoding="utf-8-sig", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["Date", "Day", "Time (ET)", "Slot", "File", "Raw URL (public)", "Facebook caption", "Instagram caption", "Facebook status", "Instagram status", "Notes"])
                w.writerows(rows)
            m += 1
            if m == 13:
                y, m = y + 1, 1
        print("csv ok")


if __name__ == "__main__":
    args = sys.argv[1:]
    root = args[0]
    src = "/tmp/claude-tool-results"
    stage = "all"
    if "--src" in args:
        src = args[args.index("--src") + 1]
    if "--stage" in args:
        stage = args[args.index("--stage") + 1]
    run(root, src, stage)
