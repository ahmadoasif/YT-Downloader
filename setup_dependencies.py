import os
import sys
import subprocess
import platform
import shutil
import zipfile
import urllib.request

def run_command(cmd, shell=False):
    try:
        subprocess.run(cmd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"? Command failed: {e}")

def install_pip_package(package):
    print(f"?? Installing {package}...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", package])

def is_installed(cmd):
    return shutil.which(cmd) is not None

def download_and_extract(url, extract_to, binary_name):
    zip_path = os.path.join(extract_to, 'temp.zip')
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(zip_path)

    bin_path = None
    for root, dirs, files in os.walk(extract_to):
        if binary_name in files:
            bin_path = os.path.join(root, binary_name)
            break
    return bin_path

def add_to_path_win(path):
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, os.environ["PATH"] + ";" + path)
    winreg.CloseKey(key)
    print(f"? Added to PATH: {path} (you may need to restart terminal)")

def install_ffmpeg():
    print("?? Checking ffmpeg...")
    if is_installed("ffmpeg"):
        print("? ffmpeg already installed.")
        return

    system = platform.system()
    if system == "Windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        target_dir = os.path.join(os.getcwd(), "ffmpeg")
        os.makedirs(target_dir, exist_ok=True)
        print("?? Downloading ffmpeg for Windows...")
        bin_path = download_and_extract(url, target_dir, "ffmpeg.exe")
        if bin_path:
            add_to_path_win(os.path.dirname(bin_path))
    elif system == "Darwin":
        run_command(["brew", "install", "ffmpeg"])
    elif system == "Linux":
        run_command(["sudo", "apt", "install", "-y", "ffmpeg"])
    else:
        print("? Unsupported OS for ffmpeg.")

def install_aria2():
    print("?? Checking aria2...")
    if is_installed("aria2c"):
        print("? aria2 already installed.")
        return

    system = platform.system()
    if system == "Windows":
        url = "https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip"
        target_dir = os.path.join(os.getcwd(), "aria2")
        os.makedirs(target_dir, exist_ok=True)
        print("?? Downloading aria2 for Windows...")
        bin_path = download_and_extract(url, target_dir, "aria2c.exe")
        if bin_path:
            add_to_path_win(os.path.dirname(bin_path))
    elif system == "Darwin":
        run_command(["brew", "install", "aria2"])
    elif system == "Linux":
        run_command(["sudo", "apt", "install", "-y", "aria2"])
    else:
        print("? Unsupported OS for aria2.")

def main():
    print("?? Setting up dependencies...")

    install_pip_package("yt-dlp")
    install_ffmpeg()
    install_aria2()

    print("\n?? All dependencies installed successfully!")

if __name__ == "__main__":
    main()
