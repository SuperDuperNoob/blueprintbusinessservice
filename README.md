# BBS — Coach Adib Portal

**Live: http://bbs.archxry.space**

Web app serving Coach Adib's Blueprint Business Service (coachadib.com) course content — lessons, HD videos, notes and quizzes — viewable directly in the browser, no login required.

## Content

- 4 programs: Blueprint Business Owner (BBO), Seni Closing Customer (SCC), Blueprint Business Service (BBS), Live Recording
- 18 courses · 50 chapters · 420 lessons (auto-synced, count grows as Coach Adib publishes)
- HD lesson videos streamed from Bunny CDN/embed, thumbnails, durations
- Lesson notes, study summaries, quizzes
- TikTok Live recordings (Jan–Mac 2026 series) as bonus course material

## Features

- Home with program cards, lesson counts and progress bars
- Program → Course → Chapter → Lesson drill-down with progress tracking
- Video player: 16:9, speed control, skip buttons, theater mode, keyboard shortcuts (space, arrows, `?`, `M`, `B`, `D`, `T`, `F`, `[`, `]`, `/`)
- Mark Done with confetti, bookmarks, next/prev lesson navigation
- Custom playlists — multi-playlist, save modal, tabs, sequential playback (YouTube/Spotify style) + Favorites with home scroll
- Global instant search across every lesson
- Day/night theme with persistence
- Everything stored client-side; works as a static site

## Update from coachadib.com

```bash
python3 sync_bbs_data.py        # pulls latest programs/courses/chapters/modules
python3 generate_offline_site.py  # rebuilds offline_site/ from bbs_data.json
git add -A && git commit -m "Sync new lessons" && git push
```

`sync_bbs_data.py` fetches the coachadib.com API (auth token from a local Chrome profile, cached fallback) and rewrites `bbs_data.json`. The push triggers GitHub Pages, which redeploys the site on the custom domain.

## Serve locally

```bash
python3 bbs_server.py           # http://localhost:5500
```

Static files from `offline_site/` plus a `/video-proxy/` route that adds the required Referer header for Bunny CDN playback. `bbs.archxry.space` is served by GitHub Pages from `offline_site/` (CNAME file).

## Files

| File | Purpose |
|---|---|
| `sync_bbs_data.py` | Pull latest content from coachadib.com API |
| `generate_offline_site.py` | Build the static site (views, player, search, playlists) |
| `bbs_server.py` | Local server with CDN referer proxy |
| `bbs_data.json` | Synced raw content (source of truth) |
| `offline_site/` | Built static site — what GitHub Pages serves |
| `launch-*.sh` / `stop-*.sh` | Local launch helpers |
