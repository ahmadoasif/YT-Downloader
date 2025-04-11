import os
import subprocess
import sys
import importlib.util
from shutil import which

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_yt_dlp():
    if importlib.util.find_spec("yt_dlp") is None:
        print("Installing yt-dlp...")
        install_package("yt-dlp")

def check_ffmpeg():
    return which("ffmpeg") is not None

def check_aria2c():
    return which("aria2c") is not None

def download_video(url, path):
    from yt_dlp import YoutubeDL

    audio_only = input("\n🔈 Do you want to download only audio? (y/N): ").strip().lower() == 'y'

    print(f"\n🔍 Fetching available formats for: {url}")
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
    except Exception as e:
        print(f"❌ Failed to fetch formats: {e}")
        input("Press Enter to continue...")
        return

    # Determine download folder based on the type (audio or video)
    if audio_only:
        download_folder = os.path.join(path if path else '.', 'Audios')
    else:
        download_folder = os.path.join(path if path else '.', 'Videos')

    # Create the folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    output_path = os.path.join(download_folder, '%(title)s.%(ext)s')

    common_options = {
        'outtmpl': output_path,
        'noplaylist': True,
        'no_mtime': True,
        'retries': 10,
        'fragment_retries': 10,
        'progress_hooks': [lambda d: print(f"Downloading... {d['_percent_str']}")],
    }

    if check_aria2c():
        common_options.update({
            'external_downloader': 'aria2c',
            'external_downloader_args': ['-x', '16', '-k', '1M'],
        })

    if audio_only:
        audio_formats = [f for f in formats if f.get('vcodec') == 'none']
        if not audio_formats:
            print("⚠️ No downloadable audio formats found.")
            input("Press Enter to continue...")
            return

        print("\n🎧 Available audio formats:")
        for idx, f in enumerate(audio_formats):
            fmt_id = f['format_id']
            abr = f.get('abr', '?')
            ext = f.get('ext', '?')
            size = f.get('filesize', 0)
            size_str = f"{size / (1024 * 1024):.2f} MB" if size else "?"
            print(f"{idx + 1}. ID: {fmt_id} | {abr} kbps | {ext} | {size_str}")

        try:
            choice = int(input("\nEnter the number of the format you want to download: ")) - 1
            selected_format = audio_formats[choice]['format_id']
        except (ValueError, IndexError):
            print("❌ Invalid choice.")
            input("Press Enter to continue...")
            return

        options = {
            'format': selected_format,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'merge_output_format': 'mp3',
        }
        options.update(common_options)

        print(f"\n🔊 Downloading audio format ID '{selected_format}'...")

    else:
        video_formats = [
            f for f in formats
            if f.get('format_id') and ('video' in f.get('format_note', '') or f.get('vcodec') != 'none')
        ]
        if not video_formats:
            print("⚠️ No downloadable video formats found.")
            input("Press Enter to continue...")
            return

        print("\n🎞️ Available video formats:")
        for idx, f in enumerate(video_formats):
            fmt_id = f['format_id']
            res = f.get('format_note', '') or f.get('height', 'unknown')
            ext = f.get('ext', '?')
            size = f.get('filesize', 0)
            size_str = f"{size / (1024 * 1024):.2f} MB" if size else "?"
            print(f"{idx + 1}. ID: {fmt_id} | {res} | {ext} | {size_str}")

        try:
            choice = int(input("\nEnter the number of the format you want to download: ")) - 1
            selected_format = video_formats[choice]['format_id']
        except (ValueError, IndexError):
            print("❌ Invalid choice.")
            input("Press Enter to continue...")
            return

        options = {
            'format': selected_format,
            'merge_output_format': 'mp4',
        }
        options.update(common_options)

        print(f"\n⬇️ Downloading video format ID '{selected_format}'...")

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        print("✅ Download completed!")
    except Exception as e:
        print(f"❌ Error during download: {e}")

    input("Press Enter to continue...")

def load_urls_from_file(file_path="videos.txt"):
    urls = []
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"❌ Could not read file: {e}")
    return urls

def main():
    ensure_yt_dlp()

    if not check_ffmpeg():
        print("⚠️ FFmpeg is not installed or not in PATH.")
        print("Download it from https://ffmpeg.org/download.html\n")

    if not check_aria2c():
        print("⚠️ aria2c not found. Download speed will be slower without it.")
        print("Download aria2 from https://github.com/aria2/aria2/releases\n")

    current_dir = os.getcwd()
    txt_path = os.path.join(current_dir, "videos.txt")

    if not os.path.exists(txt_path):
        print(f"❌ No 'videos.txt' found in {current_dir}. Exiting.")
        input("Press Enter to exit...")
        return

    print(f"Loading URLs from: {txt_path}")
    urls = load_urls_from_file(txt_path)

    if not urls:
        print("⚠️ No URLs found in 'videos.txt'. Exiting.")
        input("Press Enter to exit...")
        return

    path = input("Enter the path to save the videos (leave blank for current directory): ").strip()

    for url in urls:
        download_video(url, path)

if __name__ == "__main__":
    main()
