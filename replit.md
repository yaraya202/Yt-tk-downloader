# Media Downloader API

## Overview
A Flask-based API for downloading YouTube audio, YouTube video (360p), and TikTok videos. This project is designed to be deployed on Render.

## Project Structure
```
.
├── app.py              # Main Flask application with API endpoints
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment configuration
├── templates/
│   └── index.html      # Frontend with API documentation
└── static/
    └── style.css       # Styling for frontend
```

## API Endpoints

### YouTube
- `GET/POST /api/youtube/audio?url=<youtube_url>` - Download audio (64kbps MP3)
- `GET/POST /api/youtube/video?url=<youtube_url>` - Download video (360p)
- `GET/POST /api/youtube/info?url=<youtube_url>` - Get video info

### TikTok
- `GET/POST /api/tiktok/download?url=<tiktok_url>` - Download video
- `GET/POST /api/tiktok/info?url=<tiktok_url>` - Get video info

### Health
- `GET /health` - Health check endpoint

## Technical Details
- **Framework**: Flask 3.x
- **Download Engine**: yt-dlp
- **Production Server**: Gunicorn
- **YouTube Cookies**: Hardcoded in app.py for authentication

## Render Deployment
1. Push code to GitHub
2. Connect to Render
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`

## Recent Changes
- December 2025: Initial project setup with YouTube and TikTok download APIs
