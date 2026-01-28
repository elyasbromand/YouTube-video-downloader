import os
import sys
import subprocess
import json
import re
import time
import shutil
from pathlib import Path

def yt_dlp_base_cmd():
    """
    Base yt-dlp command with the exact flags that fixed your 403 issue in terminal.
    """
    return [
        "yt-dlp",
        "--newline",
        "--progress",
        '--extractor-args', 'youtube:player_client=android,web_embedded,tv',
        "--js-runtimes", "deno",
        "--remote-components", "ejs:github",
    ]


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
    print("=" * 70)
    print("          YOUTUBE VIDEO DOWNLOADER (No FFmpeg Required)")
    print("=" * 70)
    print()

def check_yt_dlp():
    """Check if yt-dlp is installed and up to date"""
    try:
        # Check version
        result = subprocess.run(
            ['yt-dlp', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ yt-dlp version: {result.stdout.strip()}")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ yt-dlp is not installed or not in PATH.")
        print("\nTo install yt-dlp:")
        print("   pip install yt-dlp --upgrade")
        print("\nOr download from: https://github.com/yt-dlp/yt-dlp")
        
        install = input("\nDo you want to install/update yt-dlp now? (y/n): ").lower()
        if install == 'y':
            try:
                print("\nInstalling/updating yt-dlp...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '--upgrade', '--quiet'])
                print("✅ yt-dlp installed/updated successfully!")
                return True
            except:
                print("❌ Failed to install yt-dlp. Please install manually.")
                return False
        return False
    return True

def get_valid_url():
    """Get and validate YouTube URL from user"""
    while True:
        url = input("\n📹 Paste YouTube URL (video/playlist/shorts): ").strip()
        
        if not url:
            print("❌ No URL provided. Please try again.")
            continue
        
        # Validate YouTube URL pattern
        youtube_patterns = [
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/',
            r'youtube\.com/shorts/',
            r'youtu\.be/'
        ]
        
        is_youtube_url = any(re.search(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)
        
        if is_youtube_url:
            # Ensure URL starts with http
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            return url
        else:
            print("❌ This doesn't look like a valid YouTube URL.")
            print("   Examples of valid URLs:")
            print("   - https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            print("   - https://youtu.be/dQw4w9WgXcQ")
            print("   - https://www.youtube.com/shorts/VIDEO_ID")
            print("   - https://www.youtube.com/playlist?list=PLAYLIST_ID")
            continue


#playlist check
def is_playlist_url(url):
    """Check if URL is a playlist with better detection"""
    playlist_patterns = [
        r'list=',
        r'/playlist',
        r'/watch.*list=',
        r'youtube.com/c/.*/playlists',
        r'youtube.com/user/.*/playlists'
    ]
    
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in playlist_patterns)

def get_playlist_options():
    """Get playlist download options from user"""
    print("\n🎵 Playlist Download Options:")
    print("   1. Download all videos")
    print("   2. Download specific range (e.g., 1-10)")
    print("   3. Download specific video numbers (e.g., 1,3,5)")
    print("   4. Skip already downloaded videos")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            options = {'mode': int(choice)}
            
            if choice == '2':
                while True:
                    range_input = input("Enter range (e.g., 1-10): ").strip()
                    if re.match(r'^\d+-\d+$', range_input):
                        options['range'] = range_input
                        break
                    else:
                        print("❌ Invalid range format. Use format like '1-10'")
            
            elif choice == '3':
                while True:
                    numbers_input = input("Enter video numbers (e.g., 1,3,5): ").strip()
                    if re.match(r'^\d+(,\d+)*$', numbers_input):
                        options['numbers'] = numbers_input
                        break
                    else:
                        print("❌ Invalid format. Use format like '1,3,5'")
            
            return options
        else:
            print("❌ Invalid choice. Please select 1-4.")

def get_playlist_quality():
    """Get quality options for playlist downloads"""
    print("\n📊 Playlist Quality Options:")
    print("   1. Best progressive quality (recommended)")
    print("   2. 720p HD progressive")
    print("   3. 480p progressive")
    print("   4. 360p progressive")
    
    while True:
        choice = input("\nSelect quality (1-4): ").strip()
        
        quality_map = {
            '1': 'best[ext=mp4]/best',
            '2': 'best[height<=720][ext=mp4]/best[height<=720]',
            '3': 'best[height<=480][ext=mp4]/best[height<=480]',
            '4': 'best[height<=360][ext=mp4]/best[height<=360]'
        }
        
        if choice in quality_map:
            return quality_map[choice]
        else:
            print("❌ Invalid choice. Please select 1-4.")

def get_playlist_info(url):
    """Get playlist information reliably using the same hardened yt-dlp flags."""
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
    """Download playlist using yt-dlp (uses ONLY yt-dlp) with 403-resistant flags."""
    print(f"\n🎵 Starting playlist download...")
    print(f"   Destination: {download_path}")
    print("-" * 70)

    output_template = os.path.join(
        download_path,
        "%(playlist_title)s",
        "%(playlist_index)03d - %(title)s.%(ext)s"
    )

    # Make playlist quality resistant to m3u8 fragments (same idea as your working terminal command)
    hardened_quality = (
        f"{quality}[ext=mp4][protocol!=m3u8][protocol!=m3u8_native]/"
        f"{quality}[protocol!=m3u8][protocol!=m3u8_native]/"
        "best[ext=mp4][protocol!=m3u8][protocol!=m3u8_native]/"
        "best[protocol!=m3u8][protocol!=m3u8_native]/best"
    )

    cmd = yt_dlp_base_cmd()

    cmd += ["--yes-playlist"]
    cmd += ["-o", output_template]
    cmd += ["-f", hardened_quality]

    # Playlist selection options
    if playlist_options["mode"] == 2:
        cmd += ["--playlist-items", playlist_options["range"]]
    elif playlist_options["mode"] == 3:
        cmd += ["--playlist-items", playlist_options["numbers"]]
    elif playlist_options["mode"] == 4:
        archive_file = os.path.join(download_path, "downloaded.txt")
        cmd += ["--download-archive", archive_file]

    # Reliability
    cmd += [
        "--retries", "10",
        "--fragment-retries", "10",
        "--skip-unavailable-fragments",
        "--ignore-errors",
        "--continue",
    ]

    cmd.append(url)

    print("\nRunning:", " ".join(cmd))
    print("-" * 70)

    result = subprocess.run(cmd)

    if result.returncode in (0, 1):
        print("\n✅ Playlist download finished (code:", result.returncode, ")")
        return True, "Success/Partial"
    else:
        print("\n❌ Playlist download failed (code:", result.returncode, ")")
        return False, f"Exit code {result.returncode}"


def download_playlist_alternative(url, download_path, playlist_options):
    """Alternative playlist download method"""
    try:
        # Even simpler command
        cmd = [
            'yt-dlp',
            '-o', f'{download_path}/%(playlist)s/%(title)s.%(ext)s',
            '--yes-playlist',
            '--ignore-errors',
            '--retries', '3',
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--newline',
            '--progress',
            url
        ]
        
        # Add playlist items if specified
        if playlist_options['mode'] == 2:  # Range
            cmd.insert(2, '--playlist-items')
            cmd.insert(3, playlist_options['range'])
        elif playlist_options['mode'] == 3:  # Specific numbers
            cmd.insert(2, '--playlist-items')
            cmd.insert(3, playlist_options['numbers'])
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        for line in process.stdout:
            if line.strip():
                print(f'   {line.strip()}')
        
        process.wait()
        
        return process.returncode in [0, 1]  # Accept 0 or 1 as success
        
    except Exception as e:
        print(f"❌ Alternative method failed: {e}")
        return False       

def get_download_path():
    """Get download path from user"""
    print("\n📁 Download Location:")
    print("   1. Current directory")
    print("   2. Desktop")
    print("   3. Downloads folder")
    print("   4. Videos folder")
    print("   5. Custom path")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        home = os.path.expanduser('~')
        
        if choice == '1':
            path = os.getcwd()
        elif choice == '2':
            path = os.path.join(home, 'Desktop')
        elif choice == '3':
            path = os.path.join(home, 'Downloads')
        elif choice == '4':
            path = os.path.join(home, 'Videos')
        elif choice == '5':
            path = input("Enter custom path: ").strip()
            if not path:
                print("❌ No path entered.")
                continue
            path = os.path.expanduser(path)  # Expand ~ to home directory
        else:
            print("❌ Invalid choice. Please select 1-5.")
            continue
        
        # Check if path exists
        if os.path.exists(path):
            return os.path.abspath(path)
        else:
            print(f"❌ Path '{path}' doesn't exist.")
            create = input("Create directory? (y/n): ").lower()
            if create == 'y':
                try:
                    os.makedirs(path, exist_ok=True)
                    print(f"✅ Directory created: {path}")
                    return os.path.abspath(path)
                except Exception as e:
                    print(f"❌ Could not create directory: {e}")
                    continue
            else:
                print("⚠️  Please select a different location.")
                continue

def get_video_info(url):
    """Get video information using yt-dlp (hardened flags)."""
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
    """Format duration in seconds to HH:MM:SS"""
    if not seconds:
        return "Unknown"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    else:
        return f"{minutes}m {seconds:02d}s"

def format_views(views):
    """Format view count"""
    if not views:
        return "Unknown"
    
    if views >= 1_000_000_000:
        return f"{views/1_000_000_000:.1f}B"
    elif views >= 1_000_000:
        return f"{views/1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views/1_000:.1f}K"
    else:
        return f"{views:,}"

def get_format_options():
    """Let user choose format/quality - ALL PROGRESSIVE (no FFmpeg needed)"""
    print("\n📊 Download Format Options (No FFmpeg Required):")
    print("   1. Best available progressive stream (video+audio combined)")
    print("   2. 1080p progressive (if available)")
    print("   3. 720p HD progressive")
    print("   4. 480p progressive")
    print("   5. 360p progressive")
    print("   6. Audio only - MP3 (requires FFmpeg)")
    print("   7. Audio only - best quality (requires FFmpeg)")
    print("   8. Subtitles only")
    
    while True:
        choice = input("\nSelect format (1-8): ").strip()
        
        # Progressive streams only - already combined video+audio
        format_map = {
            '1': 'best',  # This automatically picks progressive streams
            '2': 'best[height<=1080][ext=mp4]',  # MP4 progressive streams up to 1080p
            '3': 'best[height<=720][ext=mp4]',   # MP4 progressive streams up to 720p
            '4': 'best[height<=480][ext=mp4]',   # MP4 progressive streams up to 480p
            '5': 'best[height<=360][ext=mp4]',   # MP4 progressive streams up to 360p
            '6': 'bestaudio[ext=m4a]/bestaudio --extract-audio --audio-format mp3 --audio-quality 320K',
            '7': 'bestaudio',
            '8': '--write-subs --skip-download'
        }
        
        if choice in format_map:
            return format_map[choice], int(choice)
        else:
            print("❌ Invalid choice. Please select 1-8.")

def get_download_strategy():
    """Choose download strategy to overcome 403 errors"""
    print("\n🛡️  Download Strategy (to avoid blocking):")
    print("   1. Standard (recommended)")
    print("   2. Aggressive (use if Standard fails)")
    
    while True:
        choice = input("\nSelect strategy (1-2): ").strip()
        
        if choice in ['1', '2']:
            return int(choice)
        else:
            print("❌ Invalid choice. Please select 1-2.")

def download_video(url, download_path, format_choice, strategy_choice, format_num):
    """
    yt-dlp downloader hardened against YouTube SABR/HLS 403 issues.

    Key fixes:
      - Use safer YouTube player clients: android/web_embedded/tv
      - Enable EJS remote component + JS runtime (deno recommended)
      - Prefer non-m3u8 protocols to avoid fragment 403s when possible
      - Optional cookies-from-browser for gated/age/region/account cases
    """
    print(f"\n⬇️  Starting download (No FFmpeg required for formats 1-5)...")
    print(f"   Destination: {download_path}")
    print("-" * 70)

    try:
        cmd = ["yt-dlp"]

        # Output template
        output_template = os.path.join(download_path, "%(title)s.%(ext)s")
        cmd += ["-o", output_template]

        # ---- IMPORTANT: YouTube extraction hardening ----
        # Try multiple player clients. This is a common workaround when some clients only give SABR/missing URLs.
        cmd += ["--extractor-args", "youtube:player_client=android,web_embedded,tv"]  # workaround pattern :contentReference[oaicite:3]{index=3}

        # EJS / JS runtime support (recommended now; without it formats may be missing) :contentReference[oaicite:4]{index=4}
        # If you have deno installed: deno --version should work.
        cmd += ["--js-runtimes", "deno"]
        # Auto-fetch solver lib (helps with new JS challenges)
        cmd += ["--remote-components", "ejs:github"]  # shown in practice to pull solver library :contentReference[oaicite:5]{index=5}

        # OPTIONAL: if you still get 403 on some videos, uncomment cookies-from-browser:
        # cmd += ["--cookies-from-browser", "chrome"]

        # ---- FORMAT SELECTION ----
        if format_num <= 5:
            # Harden your chosen progressive format against HLS/m3u8 fragments.
            # If format_choice is like best[height<=720][ext=mp4], we prefer non-m3u8 first.
            hardened = (
                f"{format_choice}[protocol!=m3u8][protocol!=m3u8_native]/"
                "best[ext=mp4][protocol!=m3u8][protocol!=m3u8_native]/"
                "best[protocol!=m3u8][protocol!=m3u8_native]/best"
            )
            cmd += ["-f", hardened]
            cmd += ["--no-keep-video"]

        elif format_num in (6, 7):
            print("⚠️  MP3/audio extraction needs FFmpeg for conversion.")
            print("   Downloading M4A audio instead (no FFmpeg needed)...")
            cmd += ["-f", "bestaudio[ext=m4a]/bestaudio"]

        elif format_num == 8:
            cmd += ["--write-subs", "--skip-download"]

        # ---- Strategy options (keep yours, but don’t throttle too hard) ----
        if strategy_choice == 1:
            cmd += [
                "--retries", "10",
                "--fragment-retries", "10",
                "--skip-unavailable-fragments",
                "--socket-timeout", "30",
                "--force-ipv4",
                "--no-check-certificate",
                "--geo-bypass",
                "--user-agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--referer", "https://www.youtube.com/",
                "--add-header", "Accept-Language:en-US,en;q=0.9",
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
                "--user-agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--referer", "https://www.youtube.com/",
                "--add-header", "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "--add-header", "Accept-Language:en-US,en;q=0.5",
                "--add-header", "Connection:keep-alive",
                "--sleep-interval", "2",
                "--max-sleep-interval", "5",
            ]

        cmd += ["--newline", "--progress"]
        cmd.append(url)

        print("\nRunning:", " ".join(cmd))
        print("-" * 70)

        # Let yt-dlp render progress correctly
        result = subprocess.run(cmd)

        if result.returncode == 0:
            print("-" * 70)
            print("✅ Download completed successfully!")
            return True, "Success"
        elif result.returncode == 1:
            print("-" * 70)
            print("⚠️  Download partially completed (some items may have failed).")
            return True, "Partial success"
        else:
            return False, f"Download failed with exit code: {result.returncode}"

    except FileNotFoundError:
        msg = "yt-dlp not found. Please install it and ensure it's in PATH."
        print("❌", msg)
        return False, msg
    except Exception as e:
        msg = f"Download error: {e}"
        print("❌", msg)
        return False, msg


def download_playlist_without_ffmpeg(url, download_path):
    """Special function for downloading playlists without FFmpeg"""
    print("\n🎵 Downloading playlist (progressive streams only)...")
    
    try:
        cmd = [
            'yt-dlp',
            '-o', f'{download_path}/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
            '-f', 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
            '--retries', '10',
            '--fragment-retries', '10',
            '--skip-unavailable-fragments',
            '--no-playlist-reverse',
            '--no-playlist-random',
            '--download-archive', os.path.join(download_path, 'downloaded.txt'),
            '--newline',
            '--progress',
            '--console-title',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--force-ipv4',
            '--no-check-certificate',
            url
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore'
        )
        
        for line in process.stdout:
            line = line.strip()
            if '[download]' in line or '[info]' in line:
                print(f'   {line}')
        
        process.wait()
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"❌ Playlist download failed: {e}")
        return False

def main():
    """Main function"""
    if not check_yt_dlp():
        print("\n❌ Please install yt-dlp and try again.")
        input("Press Enter to exit...")
        return
    
    clear_screen()
    print_header()
    
    try:
        # Get URL
        url = get_valid_url()
        
        # Check if it's a playlist
        is_playlist = is_playlist_url(url)
        
        # Get download path
        download_path = get_download_path()
        
        # For playlists, use enhanced playlist downloader
        if is_playlist:
            print("\n🎵 Playlist detected!")
            
            # Get playlist info
            playlist_info = get_playlist_info(url)
            
            if playlist_info:
                video_count = playlist_info.get('video_count', 'unknown')
                print(f"\n📊 Playlist contains {video_count} videos")
                
                download_all = input("\nDownload this playlist? (y/n): ").lower()
                
                if download_all == 'y':
                    # Get playlist options
                    playlist_options = get_playlist_options()
                    
                    # Get quality selection
                    quality = get_playlist_quality()
                    
                    # Confirm download
                    print("\n" + "=" * 70)
                    print("PLAYLIST DOWNLOAD CONFIGURATION:")
                    print(f"   Playlist: {playlist_info['title'][:60]}..." if len(playlist_info['title']) > 60 else f"   Playlist: {playlist_info['title']}")
                    print(f"   Videos: {video_count}")
                    print(f"   Mode: {'All videos' if playlist_options['mode'] == 1 else 'Range' if playlist_options['mode'] == 2 else 'Specific numbers' if playlist_options['mode'] == 3 else 'Skip downloaded'}")
                    if playlist_options['mode'] == 2:
                        print(f"   Range: {playlist_options.get('range', 'N/A')}")
                    elif playlist_options['mode'] == 3:
                        print(f"   Videos: {playlist_options.get('numbers', 'N/A')}")
                    print(f"   Quality: {'Best' if quality == 'best[ext=mp4]/best' else '720p' if '720' in quality else '480p' if '480' in quality else '360p'}")
                    print(f"   Save to: {download_path}")
                    print("=" * 70)
                    
                    confirm = input("\n✅ Start playlist download? (y/n): ").lower()
                    if confirm != 'y':
                        print("❌ Playlist download cancelled.")
                        
                        # Ask to download another
                        print("\n" + "=" * 70)
                        another = input("📥 Download another video/playlist? (y/n): ").lower()
                        if another == 'y':
                            main()
                        else:
                            print("\n👋 Thank you for using YouTube Downloader!")
                            print("=" * 70)
                        return
                    
                    # Start playlist download
                    success, message = download_playlist(url, download_path, playlist_options, quality)
                    
                    if success:
                        print("\n🎉 Playlist download completed!")
                        print(f"📁 Playlist saved in: {download_path}")
                        
                        # Show what was downloaded
                        try:
                            # Look for downloaded files
                            import glob
                            mp4_files = glob.glob(os.path.join(download_path, "**", "*.mp4"), recursive=True)
                            webm_files = glob.glob(os.path.join(download_path, "**", "*.webm"), recursive=True)
                            m4a_files = glob.glob(os.path.join(download_path, "**", "*.m4a"), recursive=True)
                            
                            all_files = mp4_files + webm_files + m4a_files
                            if all_files:
                                print(f"\n📄 Downloaded {len(all_files)} file(s)")
                                for file in all_files[:5]:  # Show first 5
                                    filename = os.path.basename(file)
                                    size = os.path.getsize(file) / (1024*1024)
                                    print(f"   • {filename[:50]}... ({size:.1f} MB)" if len(filename) > 50 else f"   • {filename} ({size:.1f} MB)")
                                if len(all_files) > 5:
                                    print(f"   ... and {len(all_files) - 5} more")
                        except:
                            pass
                    else:
                        print(f"\n❌ Playlist download failed: {message}")
                        print("   You can try:")
                        print("   1. Check if the playlist is public")
                        print("   2. Try downloading as single videos instead")
                        print("   3. Use a different playlist URL")
                
                else:
                    print("❌ Playlist download cancelled.")
                    # Fall back to single video mode
                    print("⚠️  Falling back to single video download...")
                    # Remove playlist parameters from URL if present
                    if '&list=' in url:
                        url = url.split('&list=')[0]
                    elif '?list=' in url:
                        url = url.split('?list=')[0]
                    is_playlist = False
        
        # For single videos
        # Get video info
        print("\n🔍 Analyzing URL...")
        video_info = get_video_info(url)
        
        if video_info.get("title") != "Unknown":
            print("\n📺 Video Details:")
            print(f"   Title: {video_info.get('title', 'Unknown')}")
            print(f"   Channel: {video_info.get('uploader', 'Unknown')}")
            print(f"   Duration: {format_duration(video_info.get('duration', 0))}")
            print(f"   Views: {format_views(video_info.get('view_count', 0))}")
        
        # Get format choice
        format_choice, format_num = get_format_options()
        
        # Get download strategy
        strategy_choice = get_download_strategy()
        
        # Confirm download
        print("\n" + "=" * 70)
        print("DOWNLOAD CONFIGURATION:")
        print(f"   URL: {url[:50]}..." if len(url) > 50 else f"   URL: {url}")
        if video_info.get("title") != "Unknown":
            title = video_info.get('title', 'Unknown')
            print(f"   Title: {title[:60]}..." if len(title) > 60 else f"   Title: {title}")
        format_names = {
            1: 'Best progressive',
            2: '1080p progressive',
            3: '720p progressive',
            4: '480p progressive',
            5: '360p progressive',
            6: 'MP3 Audio (M4A fallback)',
            7: 'Best Audio (M4A fallback)',
            8: 'Subtitles only'
        }
        print(f"   Format: {format_names.get(format_num, 'Video')}")
        print(f"   Strategy: {'Standard' if strategy_choice == 1 else 'Aggressive'}")
        print(f"   Save to: {download_path}")
        print("=" * 70)
        
        confirm = input("\n✅ Start download with these settings? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Download cancelled.")
            return
        
        # Start download
        success, message = download_video(url, download_path, format_choice, strategy_choice, format_num)
        
        if success:
            print("\n🎉 Download completed successfully!")
            print(f"📁 Files saved in: {download_path}")
            
            # Show files in download directory
            try:
                files = [f for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f))]
                recent_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True)[:3]
                if recent_files:
                    print("\n📄 Recently downloaded files:")
                    for file in recent_files[:3]:
                        file_path = os.path.join(download_path, file)
                        if os.path.exists(file_path):
                            size = os.path.getsize(file_path) / (1024*1024)
                            print(f"   • {file[:50]}... ({size:.2f} MB)" if len(file) > 50 else f"   • {file} ({size:.2f} MB)")
            except:
                pass
            
            # Open folder option
            open_folder = input("\n📂 Open download folder? (y/n): ").lower()
            if open_folder == 'y':
                if os.name == 'nt':  # Windows
                    os.startfile(download_path)
                elif os.name == 'posix':  # macOS or Linux
                    if sys.platform == 'darwin':  # macOS
                        os.system(f'open "{download_path}"')
                    else:  # Linux
                        os.system(f'xdg-open "{download_path}"')
        else:
            print(f"\n❌ Download failed: {message}")
            print("   You can try:")
            print("   1. Use a different quality setting")
            print("   2. Try the aggressive strategy")
            print("   3. Check your internet connection")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

    # Ask to download another
    print("\n" + "=" * 70)
    another = input("📥 Download another video? (y/n): ").lower()
    if another == 'y':
        main()
    else:
        print("\n👋 Thank you for using YouTube Downloader!")
        print("=" * 70)

if __name__ == "__main__":
    main()