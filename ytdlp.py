#!/usr/bin/env python3
import os
import sys
import re
import json
import subprocess
from pathlib import Path
from urllib.parse import quote
import argparse
from typing import List, Dict, Optional
import time

class UniversalVideoDownloader:
    def __init__(self):
        script_dir = Path(__file__).parent.absolute()
        self.output_dir = script_dir / "Video Downloads"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.ffmpeg_path = self.find_ffmpeg_in_same_folder(script_dir)
        
        if not self.check_ytdlp_installed():
            print("[*] yt-dlp is not installed. Please install it with: python -m pip install yt-dlp")
            sys.exit(1)
    
    def find_ffmpeg_in_same_folder(self, script_dir: Path):
        ffmpeg_path = script_dir / "ffmpeg.exe"
        
        if ffmpeg_path.exists():
            return str(ffmpeg_path)
        
        for root, dirs, files in os.walk(script_dir):
            for file in files:
                if file.lower() == "ffmpeg.exe":
                    full_path = os.path.join(root, file)
                    print(f"[+] ffmpeg.exe found: {full_path}")
                    return full_path
        
        print("[!] ffmpeg.exe not found in script folder")
        print("[!] Please place ffmpeg.exe in the same folder as this script")
        print("[!] Download from: https://ffmpeg.org/download.html")
        return None
    
    def check_ytdlp_installed(self) -> bool:
        """Check if yt-dlp is installed as a Python module"""
        try:
            subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--version"], 
                capture_output=True, 
                check=True, 
                text=True, 
                timeout=10
            )
            return True
        except:
            return False
    
    def clear_screen(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.show_header()
        except Exception as e:
            print(f"[*] Error clearing screen: {e}")
    
    def show_header(self):
        try:
            print(r"       _      _ _       ")
            print(r"      | |    | | |      ")
            print(r" _   _| |_ __| | |_ __  ")
            print(r"| | | | __/ _` | | '_ \ ")
            print(r"| |_| | || (_| | | |_) |")
            print(r" \__, |\__\__,_|_| .__/ ")
            print(r"  __/ |          | |    ")
            print(r" |___/           |_|    ")
            print("     Developed by: @Finnapple")
            print()
            print("[*] Universal Video Downloader - HIGHEST QUALITY WITH AUDIO")
            print("[*] Download videos in highest quality with proper audio")
            print("[*] Supports: YouTube, Facebook, TikTok, Instagram, Twitter, etc.")
            print("[*] Paste any video URL. Type 'exit' to quit.")
            print("[*] Type 'clear' to clear the screen.")
            print(f"[*] Downloading to: {self.output_dir}")
            print("-" * 60)
        except Exception as e:
            print(f"[*] Error displaying header: {e}")
    
    def sanitize_filename(self, name: str) -> str:
        try:
            if not name:
                return "video"
            name = re.sub(r'[<>:"/\\|?*]', '', name)
            name = name.replace('｜', '-').replace('|', '-').replace('⧸', '-')
            name = name.replace('/', '-').replace('\\', '-')
            name = re.sub(r'\s+', ' ', name)
            if len(name) > 150:
                name = name[:150]
            return name.strip()
        except Exception as e:
            print(f"[*] Error sanitizing filename: {e}")
            return "video"
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[*] Getting video information (attempt {attempt + 1}/{max_retries})...")
                
                result = subprocess.run([
                    sys.executable, "-m", "yt_dlp", "--dump-json", "--no-warnings", url
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    
                    try:
                        formats_result = subprocess.run([
                            sys.executable, "-m", "yt_dlp", "-F", url
                        ], capture_output=True, text=True, timeout=30)
                        
                        lines = formats_result.stdout.split('\n')
                        best_video = None
                        best_audio = None
                        
                        for line in lines:
                            if '1080p' in line or '1440p' in line or '2160p' in line:
                                if 'video only' in line:
                                    match = re.search(r'(\d+)\s+', line)
                                    if match:
                                        best_video = match.group(1)
                            if 'audio only' in line and ('opus' in line or 'm4a' in line):
                                match = re.search(r'(\d+)\s+', line)
                                if match:
                                    best_audio = match.group(1)
                    except:
                        best_video = None
                        best_audio = None
                    
                    return {
                        'title': info.get('title', 'Unknown Title'),
                        'uploader': info.get('uploader', 'Unknown Uploader'),
                        'duration': info.get('duration', 0),
                        'view_count': info.get('view_count', 0),
                        'upload_date': info.get('upload_date', ''),
                        'description': info.get('description', '')[:200],
                        'webpage_url': info.get('webpage_url', url),
                        'extractor': info.get('extractor', 'Unknown Platform'),
                        'best_video_format': best_video,
                        'best_audio_format': best_audio
                    }
                else:
                    print(f"[*] yt-dlp returned error code: {result.returncode}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        
            except subprocess.TimeoutExpired:
                print(f"[*] Timeout getting video info (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2)
            except json.JSONDecodeError as e:
                print(f"[*] Failed to parse video info JSON: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
            except Exception as e:
                print(f"[*] Error getting video info (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print("[*] Failed to get video information after all retries")
        return None
    
    def download_with_ytdlp(self, url: str, output_path: Path, timeout: int = 900) -> bool:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                format_spec = "399+140/398+140/137+140/299+140/298+140/136+140/bestvideo+bestaudio/best"
                
                cmd = [
                    sys.executable, "-m", "yt_dlp",
                    "-f", format_spec,
                    "--merge-output-format", "mp4",
                    "--embed-metadata",
                    "--no-write-thumbnail",
                    "--no-write-info-json",
                    "--no-write-description",
                    "--no-write-annotations",
                    "--no-write-sub",
                    "--no-embed-thumbnail",
                    "-o", str(output_path / "%(title)s.%(ext)s"),
                    "--no-warnings",
                    "--newline",
                    "--progress",
                    "--verbose"  # Added verbose for better debugging
                ]
                
                if self.ffmpeg_path:
                    cmd.extend(["--ffmpeg-location", self.ffmpeg_path])
                
                cmd.append(url)
                
                print(f"[*] Download attempt {attempt + 1}/{max_retries}")
                print(f"[*] Downloading HIGHEST QUALITY (1080p/4K) with audio...")
                print(f"[*] Thumbnails and extra files DISABLED")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                start_time = time.time()
                download_completed = False
                merge_completed = False
                final_output = None
                
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        # Check for download completion
                        if '[download]' in line:
                            if '100%' in line:
                                print(f"\r{line}", flush=True)
                                # Check if this is the final destination file
                                if 'Destination' in line or 'has already been downloaded' in line:
                                    download_completed = True
                            elif 'has already been downloaded' in line:
                                print(f"[*] {line}")
                                download_completed = True
                            else:
                                # Extract and display progress
                                if '%' in line:
                                    print(f"\r{line}", end='', flush=True)
                        
                        # Check for file merging completion
                        elif 'Merging' in line:
                            print(f"\n[*] {line}")
                            if 'into' in line:
                                # Extract the output filename
                                match = re.search(r'into "(.*?)"', line)
                                if match:
                                    final_output = match.group(1)
                                    print(f"[*] Final output will be: {os.path.basename(final_output)}")
                        
                        # Check for final output message
                        elif '[Merger]' in line and 'Merged' in line:
                            print(f"[*] {line}")
                            merge_completed = True
                            download_completed = True
                        
                        # Check for successful completion message
                        elif line.startswith('[download]') and 'Downloaded' in line and 'to' in line:
                            print(f"[*] {line}")
                            download_completed = True
                        
                        # Check for final file creation
                        elif 'has already been downloaded' in line:
                            print(f"[*] {line}")
                            download_completed = True
                        
                        # Handle errors
                        elif 'ERROR' in line:
                            if 'ffprobe' in line:
                                print(f"\n[*] Using local ffmpeg for merging...")
                            else:
                                print(f"\n[!] Error: {line}")
                                if 'Video unavailable' in line or 'Private video' in line:
                                    return False
                        
                        # Handle warnings
                        elif 'WARNING' in line:
                            if 'requested format not available' in line:
                                print(f"\n[*] Format not available, trying alternative...")
                            elif 'thumbnail' not in line.lower():
                                print(f"\n[*] Warning: {line}")
                    
                    # Check for timeout
                    if time.time() - start_time > timeout:
                        process.kill()
                        print(f"\n[*] Download timed out after {timeout} seconds!")
                        if attempt < max_retries - 1:
                            print(f"[*] Retrying...")
                            time.sleep(3)
                        break
                
                # Wait for process to complete
                process.wait()
                
                # Check for successful completion
                if process.returncode == 0 or download_completed:
                    print(f"\n[+] Download completed successfully!")
                    
                    # Wait a moment for files to be written
                    time.sleep(2)
                    
                    # Find the downloaded file
                    downloaded_file = self.find_downloaded_file_by_time(output_path)
                    if downloaded_file:
                        print(f"[+] File saved as: {downloaded_file.name}")
                        
                        # Check file size
                        file_size = downloaded_file.stat().st_size / (1024 * 1024)
                        print(f"[+] File size: {file_size:.2f} MB")
                        
                        # Verify audio
                        self.verify_audio(downloaded_file)
                    else:
                        print(f"[+] Check directory for downloaded file: {output_path}")
                    
                    # Clean up temporary files
                    self.cleanup_extra_files(output_path)
                    
                    return True
                else:
                    print(f"\n[!] Download failed with exit code: {process.returncode}")
                    if attempt < max_retries - 1:
                        print(f"[*] Retrying in 3 seconds...")
                        time.sleep(3)
                    continue
                
            except Exception as e:
                print(f"[*] Error downloading with yt-dlp (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"[*] Retrying in 3 seconds...")
                    time.sleep(3)
        
        print(f"[!] Download failed after {max_retries} attempts")
        return False
    
    def find_downloaded_file_by_time(self, output_path: Path) -> Optional[Path]:
        """Find the most recently downloaded MP4 file"""
        try:
            # Get all MP4 files in the directory
            mp4_files = list(output_path.glob("*.mp4"))
            
            # Filter out temporary/partial files
            mp4_files = [f for f in mp4_files if not f.name.startswith('.') 
                        and 'part' not in f.name.lower()
                        and not any(x in f.name.lower() for x in ['temp', 'tmp', 'partial'])]
            
            if not mp4_files:
                return None
            
            # Sort by modification time (most recent first)
            mp4_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Return the most recent file
            newest_file = mp4_files[0]
            
            # Check if it was created/modified in the last 5 minutes
            current_time = time.time()
            file_time = newest_file.stat().st_mtime
            
            if current_time - file_time < 300:  # 5 minutes
                return newest_file
            else:
                # If the newest file is older than 5 minutes, check all files
                for file in mp4_files:
                    if current_time - file.stat().st_mtime < 300:
                        return file
                
                # If still no recent file, return the newest anyway
                return newest_file
                
        except Exception as e:
            print(f"[*] Error finding downloaded file: {e}")
            return None
    
    def cleanup_extra_files(self, output_path: Path):
        try:
            # Patterns for temporary/extra files to clean up
            temp_patterns = [
                "*.part", "*.temp", "*.tmp",
                "*.f399.mp4", "*.f398.mp4", "*.f137.mp4",
                "*.f140.m4a", "*.f251.webm",
                "*.ytdl", "*.ytdl-*"
            ]
            
            for pattern in temp_patterns:
                for file in output_path.glob(pattern):
                    try:
                        file.unlink()
                        print(f"[*] Removed temporary file: {file.name}")
                    except:
                        pass
            
            # Clean up thumbnail and metadata files
            other_patterns = [
                "*.jpg", "*.jpeg", "*.png", "*.webp",
                "*.info.json", "*.description",
                "*.vtt", "*.srt", "*.ass"
            ]
            
            for pattern in other_patterns:
                for file in output_path.glob(pattern):
                    try:
                        file.unlink()
                        print(f"[*] Removed extra file: {file.name}")
                    except:
                        pass
                        
        except Exception as e:
            pass  # Silently fail on cleanup errors
    
    def find_downloaded_file(self, video_info: Dict, output_path: Path) -> Optional[Path]:
        """Legacy method - kept for compatibility"""
        return self.find_downloaded_file_by_time(output_path)
    
    def verify_audio(self, file_path: Path) -> bool:
        try:
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            if self.ffmpeg_path:
                ffprobe_path = str(Path(self.ffmpeg_path).parent / "ffprobe.exe")
                if os.path.exists(ffprobe_path):
                    result = subprocess.run([
                        ffprobe_path, "-v", "quiet", "-select_streams", "a",
                        "-show_entries", "stream=codec_type", 
                        "-of", "csv=p=0", str(file_path)
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0 and 'audio' in result.stdout:
                        print(f"[+] Audio: Present ({file_size_mb:.2f} MB)")
                        return True
                    else:
                        print(f"[!] Audio: Not detected (file may be video-only)")
                        return False
            
            # Fallback check based on file size
            if file_size_mb > 50:
                print(f"[+] High quality detected: {file_size_mb:.2f} MB")
                return True
            elif file_size_mb > 20:
                print(f"[+] Standard quality: {file_size_mb:.2f} MB")
                return True
            else:
                print(f"[!] Small file size ({file_size_mb:.2f} MB) - may be low quality")
                return False
                
        except Exception as e:
            print(f"[*] Could not verify audio stream")
            return False
    
    def download_video(self, url: str) -> bool:
        try:
            print(f"[*] Processing URL: {url}")
            
            video_info = self.get_video_info(url)
            
            if video_info:
                print(f"[*] Title: {video_info['title']}")
                print(f"[*] Uploader: {video_info['uploader']}")
                print(f"[*] Platform: {video_info['extractor']}")
                if video_info['duration']:
                    minutes = int(video_info['duration']) // 60
                    seconds = int(video_info['duration']) % 60
                    print(f"[*] Duration: {minutes}:{seconds:02d}")
                if video_info['view_count']:
                    view_count = video_info['view_count']
                    if isinstance(view_count, (int, float)):
                        print(f"[*] Views: {view_count:,}")
                    else:
                        print(f"[*] Views: {view_count}")
            else:
                print("[*] Could not get video information, proceeding with download...")
                video_info = {'title': 'Unknown Video', 'uploader': 'Unknown', 'extractor': 'Unknown'}
            
            platform_dir = self.output_dir / self.sanitize_filename(video_info['extractor'])
            try:
                platform_dir.mkdir(exist_ok=True)
            except Exception as e:
                print(f"[*] Error creating directory {platform_dir}: {e}")
                platform_dir = self.output_dir
            
            print(f"[*] Downloading to: {platform_dir}")
            
            success = self.download_with_ytdlp(url, platform_dir)
            
            if success:
                print(f"[+] Download process completed successfully!")
                return True
            else:
                print("[!] Download failed after all retries")
                return False
                
        except Exception as e:
            print(f"[*] Error in download_video: {e}")
            return False
    
    def download_playlist(self, url: str) -> bool:
        try:
            print(f"[*] Processing playlist: {url}")
            
            playlist_dir = self.output_dir / "Playlists" / f"Playlist_{int(time.time())}"
            try:
                playlist_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"[*] Error creating playlist directory: {e}")
                playlist_dir = self.output_dir / "Playlists"
                playlist_dir.mkdir(exist_ok=True)
            
            print(f"[*] Downloading playlist to: {playlist_dir}")
            
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "-f", "399+140/398+140/137+140/299+140/298+140/136+140/bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "--embed-metadata",
                "--no-write-thumbnail",
                "--no-write-info-json",
                "--no-write-description",
                "--no-write-annotations",
                "--no-embed-thumbnail",
                "-o", str(playlist_dir / "%(playlist_title)s/%(title)s.%(ext)s"),
                "--no-warnings",
                "--newline",
                "--progress",
                "--verbose"
            ]
            
            if self.ffmpeg_path:
                cmd.extend(["--ffmpeg-location", self.ffmpeg_path])
            
            cmd.append(url)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            video_count = 0
            success_count = 0
            current_video = ""
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    if '[download]' in line:
                        if 'Downloading video' in line:
                            video_count += 1
                            match = re.search(r'Downloading video (\d+) of (\d+)', line)
                            if match:
                                current_video = f"Video {match.group(1)}/{match.group(2)}"
                                print(f"\n[*] Downloading {current_video}")
                        elif '100%' in line:
                            print(f"\r{line}", flush=True)
                            success_count += 1
                        elif '%' in line and 'Destination' not in line:
                            print(f"\r{line}", end='', flush=True)
                    
                    elif 'Merging' in line:
                        print(f"\n[*] {line}")
                    
                    elif '[Merger]' in line and 'Merged' in line:
                        print(f"[*] {line}")
                    
                    elif 'ERROR' in line:
                        print(f"\n[!] Error: {line}")
                    
                    elif 'WARNING' in line:
                        if 'thumbnail' not in line.lower():
                            print(f"\n[*] Warning: {line}")
            
            process.wait()
            
            self.cleanup_extra_files(playlist_dir)
            
            if process.returncode == 0:
                print(f"\n[+] Playlist download completed! Downloaded {success_count}/{video_count} videos successfully.")
                return True
            else:
                print(f"\n[!] Playlist download completed with errors. Exit code: {process.returncode}")
                print(f"[*] Successfully downloaded: {success_count}/{video_count} videos")
                return False
                
        except Exception as e:
            print(f"[*] Error downloading playlist: {e}")
            return False
    
    def process_url(self, url: str) -> bool:
        try:
            if not url.startswith(('http://', 'https://')):
                print("[!] Invalid URL format. Please include http:// or https://")
                return False
            
            if 'playlist' in url.lower() or 'list=' in url or '&list=' in url:
                print("[*] Detected playlist, downloading all videos...")
                return self.download_playlist(url)
            else:
                print("[*] Detected single video, downloading...")
                return self.download_video(url)
                
        except Exception as e:
            print(f"[*] Error processing URL: {e}")
            return False

def main():
    try:
        parser = argparse.ArgumentParser(description='Universal Video Downloader - HIGHEST QUALITY WITH AUDIO')
        parser.add_argument('url', nargs='?', help='Video URL (YouTube, Facebook, TikTok, Instagram, etc.)')
        parser.add_argument('--file', '-f', help='Text file containing multiple video URLs')
        parser.add_argument('--playlist', '-p', action='store_true', help='Force treat as playlist')
        
        args = parser.parse_args()
        
        downloader = UniversalVideoDownloader()
        
        if args.file:
            try:
                if not os.path.exists(args.file):
                    print(f"[!] File not found: {args.file}")
                    return
                
                with open(args.file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                if not urls:
                    print("[!] No URLs found in the file")
                    return
                
                print(f"[*] Found {len(urls)} URLs in file")
                success_count = 0
                
                for i, url in enumerate(urls, 1):
                    print(f"\n{'='*60}")
                    print(f"[*] Processing URL {i}/{len(urls)}: {url}")
                    print(f"{'='*60}")
                    
                    if downloader.process_url(url):
                        success_count += 1
                    
                    if i < len(urls):
                        print(f"[*] Waiting 3 seconds before next download...")
                        time.sleep(3)
                
                print(f"\n[*] Completed: {success_count}/{len(urls)} downloads successful")
                    
            except FileNotFoundError:
                print(f"[!] File not found: {args.file}")
            except PermissionError:
                print(f"[!] Permission denied accessing file: {args.file}")
            except UnicodeDecodeError:
                print(f"[!] File encoding error. Please use UTF-8 encoding: {args.file}")
            except Exception as e:
                print(f"[!] Error processing file: {e}")
        
        elif args.url:
            if args.playlist:
                downloader.download_playlist(args.url)
            else:
                downloader.process_url(args.url)
        
        else:
            downloader.show_header()
            
            while True:
                try:
                    url = input("\n[*] Enter Video URL: ").strip()
                    
                    if url.lower() in ['exit', 'quit', 'q']:
                        print("[*] Goodbye!")
                        break
                    
                    if url.lower() in ['clear', 'cls']:
                        downloader.clear_screen()
                        continue
                    
                    if not url:
                        continue
                    
                    downloader.process_url(url)
                    
                except KeyboardInterrupt:
                    print("\n[*] Exiting...")
                    break
                except EOFError:
                    print("\n[*] Exiting...")
                    break
                except Exception as e:
                    print(f"[!] Error: {e}")
    
    except KeyboardInterrupt:
        print("\n[*] Program interrupted by user")
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
