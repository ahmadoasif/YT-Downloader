import os
import subprocess
import sys
import importlib.util
from shutil import which

# --- Auto-install required packages ---
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_yt_dlp():
    if importlib.util.find_spec("yt_dlp") is None:
        print("Installing yt-dlp...")
        install_package("yt-dlp")

# --- Check for ffmpeg ---
def check_ffmpeg():
    return which("ffmpeg") is not None

# --- Download a single video ---
def download_video(url, path):
    from yt_dlp import YoutubeDL

    options = {
        'format': 'bv*+ba/b',  # best video + best audio
        'outtmpl': os.path.join(path if path else '.', '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    print(f"\n⬇️ Downloading: {url}")
    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        print("✅ Download completed!")
    except Exception as e:
        print(f"❌ Error with {url}: {str(e)}")

# --- Load URLs from .txt file (Automatically detects videos.txt) ---
def load_urls_from_file(file_path="videos.txt"):
    urls = []
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"❌ Could not read file: {e}")
    return urls

# --- Main logic ---
def main():
    ensure_yt_dlp()

    if not check_ffmpeg():
        print("⚠️  FFmpeg is not installed or not in PATH.")
        print("Please install it from https://ffmpeg.org/download.html")
        print("Video/audio may not be merged properly without it.\n")

    # Automatically load from videos.txt in the current directory
    current_dir = os.getcwd()
    txt_path = os.path.join(current_dir, "videos.txt")
    
    if not os.path.exists(txt_path):
        print(f"❌ No 'videos.txt' found in {current_dir}. Exiting.")
        return
    
    print(f"Loading URLs from: {txt_path}")
    urls = load_urls_from_file(txt_path)

    if not urls:
        print("⚠️ No URLs found in 'videos.txt'. Exiting.")
        return

    path = input("Enter the path to save the videos (leave blank for current directory): ").strip()

    for url in urls:
        download_video(url, path)

if __name__ == "__main__":
    main()
