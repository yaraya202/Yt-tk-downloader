# Media Downloader API

## Overview
A Flask-based API for downloading YouTube audio (low quality), YouTube video (360p), and TikTok videos. Ready for Render deployment.

## Project Structure
```
.
├── app.py              # Main Flask application with API endpoints
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment configuration
├── Dockerfile          # Docker deployment option
├── templates/
│   └── index.html      # Frontend with API documentation
└── static/
    └── style.css       # Styling for frontend
```

## API Endpoints

### YouTube (uses hardcoded cookies for authentication)
- `GET/POST /api/youtube/audio?url=<youtube_url>` - Download audio (64kbps MP3)
- `GET/POST /api/youtube/video?url=<youtube_url>` - Download video (360p)
- `GET/POST /api/youtube/info?url=<youtube_url>` - Get video info

### TikTok (uses tikwm API)
- `GET/POST /api/tiktok/download?url=<tiktok_url>` - Download video
- `GET/POST /api/tiktok/info?url=<tiktok_url>` - Get video info

### Health
- `GET /health` - Health check endpoint

## Technical Details
- **Framework**: Flask 3.x
- **Download Engine**: yt-dlp (YouTube), tikwm API (TikTok)
- **Audio Processing**: FFmpeg
- **Production Server**: Gunicorn
- **YouTube Cookies**: Hardcoded in app.py for authentication

## Render Deployment

### Option 1: Using render.yaml
1. Push code to GitHub
2. Connect to Render
3. It will auto-detect render.yaml

### Option 2: Manual Setup
1. Select "Web Service"
2. Runtime: Python 3
3. Build Command: `apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`

### Option 3: Docker
Use the provided Dockerfile for containerized deployment.

## Test URLs
- YouTube: https://youtu.be/Qo4IOTAbGAM
- TikTok: https://vt.tiktok.com/ZSfwk7dhv/

## Recent Changes
- December 2025: Initial project setup with YouTube and TikTok download APIs
- Added FFmpeg for audio extraction
- Added tikwm API fallback for TikTok downloads
- Added Docker support for deployment
