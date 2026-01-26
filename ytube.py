import os
import sys
import subprocess
import json
import re
import time
from pathlib import Path

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
    print("=" * 70)
    print("          YOUTUBE VIDEO DOWNLOADER (Advanced)")
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
    """Get video information using yt-dlp"""
    print("\n⏳ Fetching video information...")
    
    try:
        # Command to get video info in JSON format
        cmd = [
            'yt-dlp',
            '--skip-download',
            '--dump-json',
            '--no-warnings',
            '--no-check-certificate',
            '--force-ipv4',
            url
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print(f"⚠️  Warning: Could not fetch full video info")
            print(f"   Error: {result.stderr[:200]}")
            return {"title": "Unknown", "uploader": "Unknown", "duration": 0, "view_count": 0}
        
        # Parse JSON output
        try:
            video_info = json.loads(result.stdout)
            print("✅ Video information retrieved successfully!")
            return video_info
        except json.JSONDecodeError:
            print("⚠️  Could not parse video information, but download may still work.")
            return {"title": "Unknown", "uploader": "Unknown", "duration": 0, "view_count": 0}
        
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout while fetching video information.")
        return {"title": "Unknown", "uploader": "Unknown", "duration": 0, "view_count": 0}
    except Exception as e:
        print(f"⚠️  Error fetching video info: {str(e)[:100]}")
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
    """Let user choose format/quality"""
    print("\n📊 Download Format Options:")
    print("   1. Best quality (video + audio)")
    print("   2. 1080p HD")
    print("   3. 720p HD")
    print("   4. 480p")
    print("   5. 360p")
    print("   6. Audio only (MP3 - 320kbps)")
    print("   7. Audio only (best quality)")
    print("   8. Subtitles only")
    
    while True:
        choice = input("\nSelect format (1-8): ").strip()
        
        format_map = {
            '1': 'best',
            '2': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '3': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '4': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '5': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
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
    print("   3. Use cookies (if you have YouTube cookies file)")
    print("   4. Slow mode (for problematic videos)")
    
    while True:
        choice = input("\nSelect strategy (1-4): ").strip()
        
        if choice in ['1', '2', '3', '4']:
            return int(choice)
        else:
            print("❌ Invalid choice. Please select 1-4.")

def download_video(url, download_path, format_choice, strategy_choice, format_num):
    """Download video using yt-dlp with robust error handling"""
    print(f"\n⬇️  Starting download...")
    print(f"   Destination: {download_path}")
    print("-" * 70)
    
    try:
        # Base command
        cmd = ['yt-dlp']
        
        # Output template
        output_template = f'{download_path}/%(title)s [%(id)s].%(ext)s'
        cmd.extend(['-o', output_template])
        
        # Add format options
        if format_num == 6:  # MP3 conversion
            # Split the format string for MP3
            format_parts = format_choice.split()
            cmd.extend(format_parts)
        elif format_num == 8:  # Subtitles only
            cmd.extend(['--write-subs', '--skip-download'])
        else:
            cmd.extend(['-f', format_choice])
        
        # Add strategy-specific options
        if strategy_choice == 1:  # Standard
            cmd.extend([
                '--retries', '10',
                '--fragment-retries', '10',
                '--skip-unavailable-fragments',
                '--no-part',
                '--throttled-rate', '100K',
                '--force-ipv4',
                '--no-check-certificate',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ])
        elif strategy_choice == 2:  # Aggressive
            cmd.extend([
                '--retries', '20',
                '--fragment-retries', '20',
                '--skip-unavailable-fragments',
                '--no-part',
                '--force-ipv4',
                '--no-check-certificate',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--referer', 'https://www.youtube.com/',
                '--add-header', 'Accept-Language:en-US,en;q=0.9',
                '--sleep-interval', '2',
                '--max-sleep-interval', '5'
            ])
        elif strategy_choice == 3:  # With cookies
            cookies_path = input("Enter path to cookies.txt file: ").strip()
            if os.path.exists(cookies_path):
                cmd.extend(['--cookies', cookies_path])
            else:
                print("❌ Cookies file not found. Switching to Aggressive mode.")
                strategy_choice = 2
                return download_video(url, download_path, format_choice, 2, format_num)
        elif strategy_choice == 4:  # Slow mode
            cmd.extend([
                '--retries', '30',
                '--fragment-retries', '30',
                '--skip-unavailable-fragments',
                '--no-part',
                '--limit-rate', '500K',
                '--sleep-interval', '5',
                '--max-sleep-interval', '10',
                '--force-ipv4',
                '--no-check-certificate',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ])
        
        # Add progress and newline for better display
        cmd.extend(['--newline', '--progress'])
        
        # Add URL
        cmd.append(url)
        
        print(f"\nCommand: {' '.join(cmd[:10])}...")
        print("-" * 70)
        
        # Run download process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Display progress
        download_started = False
        last_percentage = 0
        
        for line in process.stdout:
            line = line.strip()
            
            # Show download progress
            if '[download]' in line and '%' in line:
                download_started = True
                # Extract percentage
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    percentage = float(match.group(1))
                    if percentage > last_percentage:
                        # Simple progress bar
                        bar_length = 40
                        filled = int(bar_length * percentage / 100)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f'\r   Progress: [{bar}] {percentage:.1f}%', end='', flush=True)
                        last_percentage = percentage
            elif line and not line.startswith('[debug]'):
                if download_started:
                    print(f'\n   {line}')
                else:
                    print(f'   {line}')
        
        process.wait()
        print()  # New line after progress bar
        
        if process.returncode == 0:
            print("-" * 70)
            print("✅ Download completed successfully!")
            return True, "Success"
        else:
            error_msg = "Download failed with unknown error"
            print(f"❌ {error_msg}")
            return False, error_msg
            
    except FileNotFoundError:
        error_msg = "yt-dlp not found. Please make sure it's installed."
        print(f"❌ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Download error: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def alternative_download_method(url, download_path):
    """Try alternative download method if main one fails"""
    print("\n🔄 Trying alternative download method...")
    
    try:
        # Try with different options
        cmd = [
            'yt-dlp',
            '-o', f'{download_path}/%(title)s.%(ext)s',
            '-f', 'best[height<=720]',
            '--retries', '30',
            '--fragment-retries', '30',
            '--skip-unavailable-fragments',
            '--throttled-rate', '50K',
            '--sleep-interval', '3',
            '--max-sleep-interval', '8',
            '--force-ipv4',
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '--referer', 'https://www.youtube.com/',
            '--add-header', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            '--add-header', 'Accept-Language: en-US,en;q=0.5',
            '--add-header', 'Accept-Encoding: gzip, deflate',
            '--add-header', 'DNT: 1',
            '--add-header', 'Connection: keep-alive',
            '--add-header', 'Upgrade-Insecure-Requests: 1',
            '--newline',
            '--progress',
            url
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        for line in process.stdout:
            line = line.strip()
            if line:
                print(f'   {line}')
        
        process.wait()
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"❌ Alternative method also failed: {e}")
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
        
        # Get download path
        download_path = get_download_path()
        
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
            print(f"   Title: {video_info.get('title', 'Unknown')[:60]}..." if len(video_info.get('title', '')) > 60 else f"   Title: {video_info.get('title', 'Unknown')}")
        print(f"   Format: {'MP3 Audio' if format_num == 6 else 'Subtitles' if format_num == 8 else 'Video'}")
        print(f"   Strategy: {'Standard' if strategy_choice == 1 else 'Aggressive' if strategy_choice == 2 else 'With Cookies' if strategy_choice == 3 else 'Slow Mode'}")
        print(f"   Save to: {download_path}")
        print("=" * 70)
        
        confirm = input("\n✅ Start download with these settings? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Download cancelled.")
            return
        
        # Start download
        success, message = download_video(url, download_path, format_choice, strategy_choice, format_num)
        
        if not success:
            print("\n⚠️  Primary download method failed.")
            retry = input("Try with alternative method? (y/n): ").lower()
            if retry == 'y':
                success = alternative_download_method(url, download_path)
        
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
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    # Ask to download another
    print("\n" + "=" * 70)
    another = input("📥 Download another video? (y/n): ").lower()
    if another == 'y':
        main()
    else:
        print("\n👋 Thank yaou for using YouTube Downloader!")
        print("=" * 70)

if __name__ == "__main__":
    main()