# YouTube Video Downloader — Playlists + Videos + Shorts

A terminal-based YouTube downloader built in Python using **yt-dlp**.  
Supports **single videos and playlists**, shows progress in the terminal, and is hardened against common YouTube extraction issues (e.g., HLS/SABR `403 Forbidden` fragment errors).

> ✅ For most MP4 downloads (progressive), **FFmpeg is not required**.  
> ⚠️ FFmpeg is only needed if you want MP3 conversion or merging separate audio/video streams.

---

## Features

- Download **single videos** and **playlists**
- Progress output directly in terminal (smooth and reliable)
- Playlist options:
  - Download all
  - Download range (e.g., `1-10`)
  - Download specific items (e.g., `1,3,5`)
  - Skip already-downloaded items (archive file)
- Quality selection (best / 720p / 480p / 360p)
- Hardened yt-dlp settings to reduce `403 Forbidden` issues:
  - Safer YouTube player clients (`android`, `web_embedded`, `tv`)
  - JS runtime support via **Deno**
  - Remote EJS component support (`ejs:github`)
  - Prefers non-HLS formats when possible (avoids fragment errors)

---

## Requirements

- **Python 3.8+**
- **yt-dlp**
- **Deno** (recommended / required for best reliability with YouTube)

---

## Install yt-dlp

```bash
python -m pip install -U yt-dlp
```

---

## Install Deno

```windows (wignet)
winget install DenoLand.Deno
```

---

## Verify

```bash
yt-dlp --version
deno --version
```

---

## Usage

Run the script:

```bash
python main.py
```

Then:

- Paste a YouTube video or playlist URL
- Choose download folder
- Choose playlist options (if playlist) or quality/strategy (if single video)
- Download starts with progress in the terminal

---

## Output Structure

### Playlists

Downloads into:

```
<download_path>/
  <playlist_title>/
    001 - Video Title.mp4
    002 - Video Title.mp4
    ...
```

### Single videos

Downloads into:

```
<download_path>/
  Video Title.mp4
```

---

## Common Issues & Fixes

### HTTP Error 403: Forbidden (HLS fragments)

This project uses a hardened yt-dlp setup to reduce these errors.  
If you still hit 403 on certain videos, you may need cookies (login/age/region-restricted content).

Recommended escalation (manual test):

```bash
yt-dlp --cookies-from-browser chrome "URL"
```

You can add this flag into the Python script where indicated if needed.

---

### Playlist not downloading properly

Make sure:

- You installed Deno
- yt-dlp is up to date:

```bash
python -m pip install -U yt-dlp
```

---

## Why Deno / EJS?

YouTube extraction has increasingly required a JS runtime for reliable format access.  
With Deno + EJS remote component, yt-dlp can handle newer challenges and avoid missing URLs or forced HLS/SABR-only formats.

---

## Disclaimer

This tool is for personal/educational use.  
Respect YouTube’s Terms of Service and content creators’ rights.
