# ytdlpVIDEO — Universal Video Downloader

> A fast, reliable Python-powered video downloader that supports YouTube, Facebook, TikTok, Instagram, and more — all through a simple terminal interface.

---

## Features

- Downloads high-quality video **with audio** automatically merged
- Supports **multiple platforms** — YouTube, Facebook, TikTok, Instagram, and more
- One-click installation via `setup.bat`
- Simple, clean terminal interface — no complicated setup
- Automatic audio–video merging via FFmpeg
- Beginner-friendly — **no Python experience required**

---

## Requirements

- Windows OS
- Internet connection
- [FFmpeg](https://ffmpeg.org/download.html) — download `ffmpeg.exe` and place it in the project folder (see `guide.txt` for instructions)

> Python and all other dependencies are installed automatically by `setup.bat`.

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Finnapple/ytdlpVIDEO.git
cd ytdlpVIDEO
```

### 2. Run the installer

```bash
setup.bat
```

This will automatically install Python dependencies including `yt-dlp`.

### 3. Download a video

```bash
ytdlp.bat
```

Follow the on-screen prompts, paste your video URL, and let it do the rest!

---

## Usage Guide

For detailed setup instructions (including FFmpeg installation), refer to:

```
guide.txt
```

---

## Project Structure

```
ytdlpVIDEO/
├── ytdlp.py       # Core downloader script
├── ytdlp.bat      # Main launcher
├── setup.bat      # One-click installer
└── guide.txt      # Setup & usage guide
```

---

## Supported Platforms

| Platform   | Status |
|------------|--------|
| YouTube    | Supported |
| Facebook   | Supported |
| TikTok     | Supported |
| Instagram  | Supported |
| And more…  | Supported |

> Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp), which supports [1000+ sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

---

## Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an [issue](https://github.com/Finnapple/ytdlpVIDEO/issues) or submit a pull request.

---

## License

This project is open source. See the repository for details.

---

<p align="center">Made by <a href="https://github.com/Finnapple">Finnapple</a></p>
