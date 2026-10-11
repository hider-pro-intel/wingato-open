# Wingato Open

A free downloader for **openly-licensed and public-domain media**, built
with Flask. It searches the Internet Archive and Wikimedia Commons and
streams films, audio, images and text straight to the user.

Unlike a general video downloader, it only touches libraries whose
content is free to reuse and whose APIs permit downloading — which is what
lets it stay online and accept mainstream advertising.

## Why this version

A site that scrapes YouTube / Instagram / Facebook / X runs into three
walls at once: cloud hosts suspend it, the platforms block datacenter IPs,
and ad networks reject it. Sourcing from open libraries avoids all three.

## Run locally

```bash
pip install -r requirements.txt
python app.py            # http://127.0.0.1:5000
```

On Windows, double-click **run.bat**.

No ffmpeg and no yt-dlp needed — files are streamed directly from the
source libraries.

## Routes

| Route | Purpose |
|-------|---------|
| `/` | Home + search |
| `/search?q=&source=` | Results (source = all / archive / commons) |
| `/item?id=` | An Internet Archive item's file list |
| `/download?url=&name=` | Streams a file (allowlisted hosts only) |
| `/about`, `/contact` | Info pages |

## Sources & licensing

- **Internet Archive** — public-domain and CC media. Each item links to its
  source page showing the exact licence.
- **Wikimedia Commons** — public-domain and CC media (CC0, CC-BY, etc.).
  CC-BY requires attribution; the source page has the details.

Wingato hosts nothing. Every download is a direct stream from the library.

## Deploy

See `DEPLOY.md`. Short version: push to GitHub, then create a Render
Blueprint — `render.yaml` and the `Dockerfile` are included.

## Security notes

- Downloads are restricted to an allowlist of source hosts
  (`archive.org`, `upload.wikimedia.org`, `commons.wikimedia.org`), so the
  `/download` endpoint cannot be used as an open proxy.
- Rate limited (60/hour, 30/min on search, 20/min on download).
- No user accounts, no database, no stored files.

## Monetisation

Ad slots are marked in the templates (`.ad-slot`). Because the content is
legal and family-safe, mainstream networks (AdSense, Ezoic, etc.) will
accept the site — the thing that blocked ads on a scraping downloader.
Realistic early revenue is modest; treat ads as a top-up, not a salary.
