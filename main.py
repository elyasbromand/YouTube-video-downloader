import os
import sys
import subprocess
import json
import re


# ---------------------------
# yt-dlp hardened base command
# ---------------------------
def yt_dlp_base_cmd():
    """
    Base yt-dlp command with the exact flags that fixed your 403 issue in terminal.
    Keep ALL yt-dlp calls consistent by using this everywhere.
    """
    return [
        "yt-dlp",
        "--newline",
        "--progress",
        "--extractor-args",
        "youtube:player_client=android,web_embedded,tv",
        "--js-runtimes",
        "deno",
        "--remote-components",
        "ejs:github",
    ]


# ---------------------------
# UI helpers
# ---------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    print("=" * 70)
    print("          YOUTUBE VIDEO DOWNLOADER (No FFmpeg Required)")
    print("=" * 70)
    print()


# ---------------------------
# Environment checks
# ---------------------------
def check_yt_dlp():
    """Check if yt-dlp is installed and up to date."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            print(f"✅ yt-dlp version: {result.stdout.strip()}")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("❌ yt-dlp is not installed or not in PATH.")
    print("\nTo install yt-dlp:")
    print("   python -m pip install yt-dlp --upgrade")
    print("\nOr download from: https://github.com/yt-dlp/yt-dlp")

    install = input("\nDo you want to install/update yt-dlp now? (y/n): ").lower()
    if install == "y":
        try:
            print("\nInstalling/updating yt-dlp...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "yt-dlp", "--upgrade", "--quiet"],
                check=False,
            )
            # Re-check
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="ignore",
            )
            if result.returncode == 0:
                print(f"✅ yt-dlp version: {result.stdout.strip()}")
                return True
        except Exception:
            pass

    print("❌ Failed to install/update yt-dlp. Please install manually.")
    return False


# ---------------------------
# URL handling
# ---------------------------
def get_valid_url():
    """Get and validate YouTube URL from user."""
    while True:
        url = input("\n📹 Paste YouTube URL (video/playlist/shorts): ").strip()
        if not url:
            print("❌ No URL provided. Please try again.")
            continue

        youtube_patterns = [
            r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/",
            r"youtube\.com/shorts/",
            r"youtu\.be/",
        ]

        if any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns):
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            return url

        print("❌ This doesn't look like a valid YouTube URL.")
        print("   Examples:")
        print("   - https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        print("   - https://youtu.be/dQw4w9WgXcQ")
        print("   - https://www.youtube.com/shorts/VIDEO_ID")
        print("   - https://www.youtube.com/playlist?list=PLAYLIST_ID")


def is_playlist_url(url: str) -> bool:
    playlist_patterns = [
        r"list=",
        r"/playlist",
        r"/watch.*list=",
        r"youtube.com/c/.*/playlists",
        r"youtube.com/user/.*/playlists",
    ]
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in playlist_patterns)


# ---------------------------
# Download path
# ---------------------------
def get_download_path():
    print("\n📁 Download Location:")
    print("   1. Current directory")
    print("   2. Desktop")
    print("   3. Downloads folder")
    print("   4. Videos folder")
    print("   5. Custom path")

    while True:
        choice = input("\nSelect option (1-5): ").strip()
        home = os.path.expanduser("~")

        if choice == "1":
            path = os.getcwd()
        elif choice == "2":
            path = os.path.join(home, "Desktop")
        elif choice == "3":
            path = os.path.join(home, "Downloads")
        elif choice == "4":
            path = os.path.join(home, "Videos")
        elif choice == "5":
            path = input("Enter custom path: ").strip()
            if not path:
                print("❌ No path entered.")
                continue
            path = os.path.expanduser(path)
        else:
            print("❌ Invalid choice. Please select 1-5.")
            continue

        if os.path.exists(path):
            return os.path.abspath(path)

        print(f"❌ Path '{path}' doesn't exist.")
        create = input("Create directory? (y/n): ").lower()
        if create == "y":
            try:
                os.makedirs(path, exist_ok=True)
                print(f"✅ Directory created: {path}")
                return os.path.abspath(path)
            except Exception as e:
                print(f"❌ Could not create directory: {e}")


# ---------------------------
# Playlist options
# ---------------------------
def get_playlist_options():
    print("\n🎵 Playlist Download Options:")
    print("   1. Download all videos")
    print("   2. Download specific range (e.g., 1-10)")
    print("   3. Download specific video numbers (e.g., 1,3,5)")
    print("   4. Skip already downloaded videos")

    while True:
        choice = input("\nSelect option (1-4): ").strip()
        if choice not in ["1", "2", "3", "4"]:
            print("❌ Invalid choice. Please select 1-4.")
            continue

        options = {"mode": int(choice)}

        if choice == "2":
            while True:
                range_input = input("Enter range (e.g., 1-10): ").strip()
                if re.match(r"^\d+-\d+$", range_input):
                    options["range"] = range_input
                    break
                print("❌ Invalid range format. Use format like '1-10'")

        if choice == "3":
            while True:
                numbers_input = input("Enter video numbers (e.g., 1,3,5): ").strip()
                if re.match(r"^\d+(,\d+)*$", numbers_input):
                    options["numbers"] = numbers_input
                    break
                print("❌ Invalid format. Use format like '1,3,5'")

        return options


def get_playlist_quality():
    print("\n📊 Playlist Quality Options:")
    print("   1. Best progressive quality (recommended)")
    print("   2. 720p HD progressive")
    print("   3. 480p progressive")
    print("   4. 360p progressive")

    quality_map = {
        "1": "best[ext=mp4]/best",
        "2": "best[height<=720][ext=mp4]/best[height<=720]",
        "3": "best[height<=480][ext=mp4]/best[height<=480]",
        "4": "best[height<=360][ext=mp4]/best[height<=360]",
    }

    while True:
        choice = input("\nSelect quality (1-4): ").strip()
        if choice in quality_map:
            return quality_map[choice]
        print("❌ Invalid choice. Please select 1-4.")


def get_playlist_info(url):
    print("\n⏳ Fetching playlist information...")

    try:
        cmd = yt_dlp_base_cmd() + [
            "--flat-playlist",
            "--dump-single-json",
            "--no-warnings",
            url,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            entries = data.get("entries") or []
            title = data.get("title") or data.get("playlist_title") or "Unknown Playlist"
            print(f"✅ Found playlist: {title} ({len(entries)} videos)")
            return {"title": title, "video_count": len(entries), "method": "json"}

        print("⚠️  Could not fetch detailed playlist info (continuing anyway).")
        return {"title": "YouTube Playlist", "video_count": "unknown", "method": "fallback"}

    except Exception as e:
        print(f"⚠️  Could not get detailed playlist info: {str(e)[:120]}")
        return {"title": "YouTube Playlist", "video_count": "unknown", "method": "error"}


def download_playlist(url, download_path, playlist_options, quality):
    print(f"\n🎵 Starting playlist download...")
    print(f"   Destination: {download_path}")
    print("-" * 70)

    output_template = os.path.join(
        download_path,
        "%(playlist_title)s",
        "%(playlist_index)03d - %(title)s.%(ext)s",
    )

    hardened_quality = (
        f"{quality}[ext=mp4][protocol!=m3u8][protocol!=m3u8_native]/"
        f"{quality}[protocol!=m3u8][protocol!=m3u8_native]/"
        "best[ext=mp4][protocol!=m3u8][protocol!=m3u8_native]/"
        "best[protocol!=m3u8][protocol!=m3u8_native]/best"
    )

    cmd = yt_dlp_base_cmd() + [
        "--yes-playlist",
        "-o", output_template,
        "-f", hardened_quality,
        "--retries", "10",
        "--fragment-retries", "10",
        "--skip-unavailable-fragments",
        "--ignore-errors",
        "--continue",
    ]

    if playlist_options["mode"] == 2:
        cmd += ["--playlist-items", playlist_options["range"]]
    elif playlist_options["mode"] == 3:
        cmd += ["--playlist-items", playlist_options["numbers"]]
    elif playlist_options["mode"] == 4:
        archive_file = os.path.join(download_path, "downloaded.txt")
        cmd += ["--download-archive", archive_file]

    cmd.append(url)

    print("\nRunning:", " ".join(cmd))
    print("-" * 70)

    result = subprocess.run(cmd)

    if result.returncode in (0, 1):
        print("\n✅ Playlist download finished (code:", result.returncode, ")")
        return True, "Success/Partial"
    return False, f"Exit code {result.returncode}"


# ---------------------------
# Single video info + download
# ---------------------------
def get_video_info(url):
    print("\n⏳ Fetching video information...")

    try:
        cmd = yt_dlp_base_cmd() + [
            "--skip-download",
            "--dump-json",
            "--no-warnings",
            url,
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0 or not result.stdout.strip():
            print("⚠️  Warning: Could not fetch full video info (download may still work).")
            return {"title": "Unknown", "uploader": "Unknown", "duration": 0, "view_count": 0}

        return json.loads(result.stdout)

    except Exception as e:
        print(f"⚠️  Error fetching video info: {str(e)[:120]}")
        return {"title": "Unknown", "uploader": "Unknown", "duration": 0, "view_count": 0}


def format_duration(seconds):
    if not seconds:
        return "Unknown"
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    return f"{minutes}m {seconds:02d}s"


def format_views(views):
    if not views:
        return "Unknown"
    views = int(views)
    if views >= 1_000_000_000:
        return f"{views/1_000_000_000:.1f}B"
    if views >= 1_000_000:
        return f"{views/1_000_000:.1f}M"
    if views >= 1_000:
        return f"{views/1_000:.1f}K"
    return f"{views:,}"


def get_format_options():
    print("\n📊 Download Format Options (No FFmpeg Required):")
    print("   1. Best available progressive stream (video+audio combined)")
    print("   2. 1080p progressive (if available)")
    print("   3. 720p HD progressive")
    print("   4. 480p progressive")
    print("   5. 360p progressive")
    print("   6. Audio only (M4A, no FFmpeg)")
    print("   7. Best audio (M4A preferred, no FFmpeg)")
    print("   8. Subtitles only")

    format_map = {
        "1": ("best", 1),
        "2": ("best[height<=1080][ext=mp4]", 2),
        "3": ("best[height<=720][ext=mp4]", 3),
        "4": ("best[height<=480][ext=mp4]", 4),
        "5": ("best[height<=360][ext=mp4]", 5),
        "6": ("bestaudio[ext=m4a]/bestaudio", 6),
        "7": ("bestaudio[ext=m4a]/bestaudio", 7),
        "8": ("SUBS_ONLY", 8),
    }

    while True:
        choice = input("\nSelect format (1-8): ").strip()
        if choice in format_map:
            return format_map[choice]
        print("❌ Invalid choice. Please select 1-8.")


def get_download_strategy():
    print("\n🛡️  Download Strategy (to avoid blocking):")
    print("   1. Standard (recommended)")
    print("   2. Aggressive (use if Standard fails)")
    while True:
        choice = input("\nSelect strategy (1-2): ").strip()
        if choice in ["1", "2"]:
            return int(choice)
        print("❌ Invalid choice. Please select 1-2.")


def download_video(url, download_path, format_choice, strategy_choice, format_num):
    print(f"\n⬇️  Starting download (No FFmpeg required for most modes)...")
    print(f"   Destination: {download_path}")
    print("-" * 70)

    output_template = os.path.join(download_path, "%(title)s.%(ext)s")

    cmd = yt_dlp_base_cmd() + ["-o", output_template]

    if format_num == 8:  # subtitles only
        cmd += ["--write-subs", "--skip-download"]
    else:
        # Avoid m3u8/hls fragments whenever possible (same concept as playlist)
        hardened = (
            f"{format_choice}[protocol!=m3u8][protocol!=m3u8_native]/"
            "best[ext=mp4][protocol!=m3u8][protocol!=m3u8_native]/"
            "best[protocol!=m3u8][protocol!=m3u8_native]/best"
        )
        cmd += ["-f", hardened]
        cmd += ["--no-keep-video"]

    # Strategy options
    if strategy_choice == 1:
        cmd += [
            "--retries", "10",
            "--fragment-retries", "10",
            "--skip-unavailable-fragments",
            "--socket-timeout", "30",
            "--force-ipv4",
            "--no-check-certificate",
            "--geo-bypass",
            "--referer", "https://www.youtube.com/",
        ]
    else:
        cmd += [
            "--retries", "20",
            "--fragment-retries", "20",
            "--skip-unavailable-fragments",
            "--socket-timeout", "60",
            "--force-ipv4",
            "--no-check-certificate",
            "--geo-bypass",
            "--referer", "https://www.youtube.com/",
            "--sleep-interval", "2",
            "--max-sleep-interval", "5",
        ]

    # If you ever need login-based access, uncomment:
    # cmd += ["--cookies-from-browser", "chrome"]

    cmd.append(url)

    print("\nRunning:", " ".join(cmd))
    print("-" * 70)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("-" * 70)
        print("✅ Download completed successfully!")
        return True, "Success"
    if result.returncode == 1:
        print("-" * 70)
        print("⚠️  Download partially completed (some items may have failed).")
        return True, "Partial success"
    return False, f"Download failed with exit code: {result.returncode}"


# ---------------------------
# Main
# ---------------------------
def main():
    if not check_yt_dlp():
        input("Press Enter to exit...")
        return

    clear_screen()
    print_header()

    try:
        url = get_valid_url()
        download_path = get_download_path()

        if is_playlist_url(url):
            print("\n🎵 Playlist detected!")
            playlist_info = get_playlist_info(url)
            video_count = playlist_info.get("video_count", "unknown")
            print(f"\n📊 Playlist contains {video_count} videos")

            if input("\nDownload this playlist? (y/n): ").lower() != "y":
                print("❌ Playlist download cancelled.")
                return

            playlist_options = get_playlist_options()
            quality = get_playlist_quality()

            print("\n" + "=" * 70)
            print("PLAYLIST DOWNLOAD CONFIGURATION:")
            print(f"   Playlist: {playlist_info['title']}")
            print(f"   Videos: {video_count}")
            print(f"   Save to: {download_path}")
            print("=" * 70)

            if input("\n✅ Start playlist download? (y/n): ").lower() != "y":
                print("❌ Playlist download cancelled.")
                return

            success, message = download_playlist(url, download_path, playlist_options, quality)
            if not success:
                print(f"\n❌ Playlist download failed: {message}")
            else:
                print("\n🎉 Playlist download completed!")
                print(f"📁 Saved in: {download_path}")
            return

        # Single video flow
        print("\n🔍 Analyzing URL...")
        video_info = get_video_info(url)

        if video_info.get("title") != "Unknown":
            print("\n📺 Video Details:")
            print(f"   Title: {video_info.get('title', 'Unknown')}")
            print(f"   Channel: {video_info.get('uploader', 'Unknown')}")
            print(f"   Duration: {format_duration(video_info.get('duration', 0))}")
            print(f"   Views: {format_views(video_info.get('view_count', 0))}")

        format_choice, format_num = get_format_options()
        strategy_choice = get_download_strategy()

        print("\n" + "=" * 70)
        print("DOWNLOAD CONFIGURATION:")
        print(f"   URL: {url}")
        print(f"   Save to: {download_path}")
        print("=" * 70)

        if input("\n✅ Start download with these settings? (y/n): ").lower() != "y":
            print("❌ Download cancelled.")
            return

        success, message = download_video(url, download_path, format_choice, strategy_choice, format_num)
        if not success:
            print(f"\n❌ Download failed: {message}")
        else:
            print("\n🎉 Download completed successfully!")
            print(f"📁 Files saved in: {download_path}")

            open_folder = input("\n📂 Open download folder? (y/n): ").lower()
            if open_folder == "y" and os.name == "nt":
                os.startfile(download_path)

    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
