import json
import os
import sys
from datetime import datetime
from yt_dlp import YoutubeDL

# Load config
CONFIG_PATH = 'config.json'
if not os.path.exists(CONFIG_PATH):
    print("❌ Config file not found.")
    sys.exit(1)

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

preferred_quality = config.get("preferred_quality", "1080p").replace("p", "")
playlist_mode = config.get("playlist_mode", False)
use_external_downloader = config.get("use_external_downloader", False)

# Ensure Videos folder exists
os.makedirs('Videos', exist_ok=True)

# Log file (store in same directory as script)
LOG_FILE = os.path.join(os.path.dirname(__file__), 'download_log.txt')

# Build format string with fallback to lower quality
def build_format_string():
    fallback_qualities = [1080, 720, 480, 360, 240, 144]
    quality_list = [q for q in fallback_qualities if q <= int(preferred_quality)]

    format_list = []
    for q in quality_list:
        format_string = (
            f"bestvideo[height={q}][ext=mp4]+bestaudio[ext=m4a]/"
            f"best[height={q}][ext=mp4]/"
            f"best[height<={q}][ext=mp4]"
        )
        format_list.append(format_string)

    return "/".join(format_list)

# yt-dlp options
ydl_opts = {
    'format': build_format_string(),
    'outtmpl': 'Videos/%(title)s.%(ext)s',  # Download directly to Videos folder
    'noplaylist': not playlist_mode,
    'merge_output_format': 'mp4',
    'quiet': False,
    'no_warnings': True,
}

# External downloader support
if use_external_downloader:
    ydl_opts.update({
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '16', '-k', '1M']
    })

# Log downloaded video info
def log_download(info):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = info.get('title', 'Unknown')
    resolution = info.get('resolution', f"{info.get('height', 'Unknown')}p")
    format_id = info.get('format', 'Unknown')

    log_entry = f"[{now}] Title: {title} | Resolution: {resolution} | Format: {format_id}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)

# Show downloaded quality
def show_downloaded_quality(info):
    video_format = info.get('format', 'Unknown')
    height = info.get('height', 'Unknown')
    resolution = info.get('resolution', f"{height}p")
    has_audio = info.get('acodec', 'none') != 'none'
    has_video = info.get('vcodec', 'none') != 'none'

    print("\n✅ Download Summary:")
    print(f"📹 Title: {info.get('title', 'Unknown')}")
    print(f"🎞️  Format: {video_format}")
    print(f"📏 Resolution: {resolution}")
    print(f"🔊 Audio: {'Yes' if has_audio else 'No'}")
    print(f"🎥 Video: {'Yes' if has_video else 'No'}")
    print("-" * 40)

# Download function
def download_video(url):
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            entries = info['entries'] if 'entries' in info else [info]

            for entry in entries:
                show_downloaded_quality(entry)
                log_download(entry)

        except Exception as e:
            print(f"❌ Error downloading video: {e}")

# Entry point
if __name__ == "__main__":
    if not os.path.exists("videos.txt"):
        print("❌ videos.txt file not found.")
        input("Press Enter to exit...")
        sys.exit(1)

    with open("videos.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("❌ videos.txt is empty.")
        input("Press Enter to exit...")
        sys.exit(1)

    print(f"🔽 Starting download of {len(urls)} video(s)...")
    for url in urls:
        print(f"\n📥 Downloading: {url}")
        download_video(url)

    print("\n✅ All downloads finished!")
    input("Press Enter to exit...")
