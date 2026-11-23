# Ticket Closed: IT Memes - content assets (public)

Public host for post media so Windsor.ai can fetch it by URL. Raw URL:
`https://raw.githubusercontent.com/11001001100001111011011101101100100/ticket-closed-assets/main/<path>`

## Layout
`<year>/<MM-Month>/{daily-news,daily-meme,daily-fix,daily-reel}/` plus `schedule.csv` in each month.
Nov 2026 to Dec 2027. Files are named date first:
- `YYYY-MM-DD_news.txt|png|jpg` 6:00 AM satire card (made that morning)
- `YYYY-MM-DD_meme.png|jpg|txt` 12:00 PM, 1080x1080 (use the JPG for Instagram)
- `YYYY-MM-DD_fix.jpg|txt` 2:00 PM, 1080x1350, FB and IG captions in the txt
- `YYYY-MM-DD_reel.mp4|txt` 8:00 PM, 1080x1920, about 11 s

`schedule.csv` columns: Date, Day, Time, Slot, File, Raw URL, FB caption, IG caption, FB status, IG status, Notes.

## Status
Memes/Reels made through 2027-01-31 (Nov 19 on), Fix of the Day through 2027-01-31. Feb to Dec 2027 are empty skeleton rows.
`tools/` holds the generators (meme_factory, fix_card, data files, build_month_tree). Do not put private files here: the repo is public.
`reels/ticket_closed_reel_5.mp4` is temporary (tonight's Instagram Reel) and gets deleted after it posts.
