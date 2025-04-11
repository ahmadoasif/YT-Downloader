# ?? YoutubeDownloader.py

A simple Python script to download audio or video from YouTube links listed in a text file.  
You can choose to download either audio (converted to MP3) or full video using `yt-dlp`, `ffmpeg`, and optionally `aria2c` for faster downloads.

---

## ?? Requirements

- Python (3.6 or higher recommended)  
- [ffmpeg](https://ffmpeg.org/download.html) – for audio conversion  
- (Optional) [aria2c](https://github.com/aria2/aria2/releases) – for faster external downloading  
- `yt-dlp` (auto-installed by the script if missing)

---

## ?? Usage

1. Download or clone this repository.
2. Create a `videos.txt` file in the **same directory** as `YoutubeDownloader.py`.
3. Paste your video links in this file — one link per line.
4. Run the script:
   ```bash
   python YoutubeDownloader.py


