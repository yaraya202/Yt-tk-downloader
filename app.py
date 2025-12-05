from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp
import requests
import re
import os
import tempfile
import uuid

app = Flask(__name__)

YOUTUBE_COOKIES = "__Secure-YNID=13.YT=Jkg0SXBKvrrT-XJS7XLc6BLgoAnhYBiaL4Dn6YPXqjxUVSxByT-l62c19MNQsmNeycItgBeXYAgGE4oxsoAnZ-urRqaYUpSl_Nt0slZ1Qqgu68u_kDOnIufobqBP1GVPBbDmaUPD8poNw2EalIksY-WlwVIfdttllzFBHpUAvx7wvTvyG_E-84Zg-pWL7Yrwd1jz8wGDL-YHQBknTSL6SuoEE0G7w4P7WF-5Ua8IuNtov5wzJuAO3kOnK3ddMsxIb1eJKj8F8l32gNuL6rsL1AGRtyQ6CP7avkih10ldSKGx64lyqf2W38iGdi4h7RwrjpLerl5Y9k0Vr86Ui9iZJQ; YSC=oUhngLIFCWo; VISITOR_INFO1_LIVE=2L8cVCCuRGs; VISITOR_PRIVACY_METADATA=CgJQSxIEGgAgNQ%3D%3D; VISITOR_INFO1_LIVE=2L8cVCCuRGs; VISITOR_PRIVACY_METADATA=CgJQSxIEGgAgNQ%3D%3D; __Secure-1PSIDTS=sidts-CjQBwQ9iI9fswdyNcfpuSMEtQQEV3z1UmSqhPISIWiUbHEcqpF3tkTuT5NvIWAVP0pIbH77HEAA; __Secure-3PSIDTS=sidts-CjQBwQ9iI9fswdyNcfpuSMEtQQEV3z1UmSqhPISIWiUbHEcqpF3tkTuT5NvIWAVP0pIbH77HEAA; __Secure-3PAPISID=F51XTRZi6unq_cWQ/A9jQ53W-CvZsBV_yD; __Secure-3PSID=g.a0003Qjfd0T69Q9L0kVRT7ygUusNVHl5N3MeSgvq-tw_S8r0pZLRv645_ZmbEi6xupub8VVWFQACgYKAeISARUSFQHGX2Mib6jLchg-nZ21mtRzXQrPTRoVAUF8yKrkr51jnMTdldIC1LHJEMvX0076; LOGIN_INFO=AFmmF2swRAIgEcknGtlOz5SE_xHlJW88_Bv-SrxoAGdESc6UtWfk428CIEckjC2WIBIBX3-snwfRusRHoJbh3aUQc5btNAyaZxdw:QUQ3MjNmellhZng0eURUVU5ZUEtMcEsta1VPbHgzTDVzRHQ4ZnEtXzVMX2lEUl9jUHVIYU9NSzZtUU1GZU9TTVh4U19Sa3NpYmtmUzBCdDFmeUlsd1VoVmV5RFUxNWhGM01DV0xtbmZCemRxR01KZThJdDJKWkJrcTZxSWNGVTZPVHllYmQtR3A1SmFlQ3lQcS1FRkNGSktzZVdUX08wLWdn; PREF=f4=4000000&f6=40000000&tz=Asia.Karachi&f7=100; __Secure-ROLLOUT_TOKEN=CIqKztuHvPuDFBCDn73Ms-yQAxjK99XujaeRAw%3D%3D; __Secure-3PSIDCC=AKEyXzVUgDi3PVCGnbsXrX5OKQkv4rdxFEnFgDpZSoMSCCLT6YwE2mLSZTSYkDjZkQTdGmrzUQ"

TIKTOK_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.tiktok.com/',
}

def create_cookie_file():
    cookie_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    cookie_file.write("# Netscape HTTP Cookie File\n")
    cookie_file.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
    cookie_file.write("# This is a generated file!  Do not edit.\n\n")
    
    cookies = YOUTUBE_COOKIES.split('; ')
    for cookie in cookies:
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookie_file.write(f".youtube.com\tTRUE\t/\tTRUE\t2147483647\t{name}\t{value}\n")
    
    cookie_file.close()
    return cookie_file.name

def get_yt_dlp_options(format_type, output_path):
    cookie_file = create_cookie_file()
    
    base_options = {
        'cookiefile': cookie_file,
        'quiet': True,
        'no_warnings': True,
        'outtmpl': output_path,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if format_type == 'audio':
        base_options.update({
            'format': 'worstaudio/worst',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }],
        })
    elif format_type == 'video':
        base_options.update({
            'format': 'best[height<=360]/worst',
        })
    
    return base_options, cookie_file


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/youtube/audio', methods=['GET', 'POST'])
def youtube_audio():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:
        url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required', 'success': False}), 400
    
    try:
        temp_dir = tempfile.mkdtemp()
        unique_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(temp_dir, f'audio_{unique_id}.%(ext)s')
        
        options, cookie_file = get_yt_dlp_options('audio', output_path)
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
            
        final_path = os.path.join(temp_dir, f'audio_{unique_id}.mp3')
        
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
        
        if os.path.exists(final_path):
            return send_file(
                final_path,
                as_attachment=True,
                download_name=f'{title}.mp3',
                mimetype='audio/mpeg'
            )
        
        for file in os.listdir(temp_dir):
            if file.startswith(f'audio_{unique_id}'):
                return send_file(
                    os.path.join(temp_dir, file),
                    as_attachment=True,
                    download_name=f'{title}.mp3',
                    mimetype='audio/mpeg'
                )
        
        return jsonify({'error': 'Audio file not found', 'success': False}), 500
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/youtube/video', methods=['GET', 'POST'])
def youtube_video():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:
        url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required', 'success': False}), 400
    
    try:
        temp_dir = tempfile.mkdtemp()
        unique_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(temp_dir, f'video_{unique_id}.%(ext)s')
        
        options, cookie_file = get_yt_dlp_options('video', output_path)
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
        
        for file in os.listdir(temp_dir):
            if file.startswith(f'video_{unique_id}'):
                return send_file(
                    os.path.join(temp_dir, file),
                    as_attachment=True,
                    download_name=f'{title}.{ext}',
                    mimetype='video/mp4'
                )
        
        return jsonify({'error': 'Video file not found', 'success': False}), 500
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/youtube/info', methods=['GET', 'POST'])
def youtube_info():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:
        url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required', 'success': False}), 400
    
    try:
        cookie_file = create_cookie_file()
        
        options = {
            'cookiefile': cookie_file,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
        
        return jsonify({
            'success': True,
            'title': info.get('title'),
            'duration': info.get('duration'),
            'thumbnail': info.get('thumbnail'),
            'description': info.get('description', '')[:500],
            'uploader': info.get('uploader'),
            'view_count': info.get('view_count'),
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


def download_tiktok_via_api(url):
    api_url = f"https://tikwm.com/api/?url={url}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        response = requests.get(api_url, headers=headers, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            video_data = data.get('data', {})
            author_info = video_data.get('author', {})
            return {
                'success': True,
                'title': video_data.get('title', 'TikTok Video'),
                'author': author_info.get('nickname', 'Unknown') if isinstance(author_info, dict) else 'Unknown',
                'video_url': video_data.get('play', ''),
                'thumbnail': video_data.get('cover', ''),
                'duration': video_data.get('duration', 0),
                'music': video_data.get('music', ''),
            }
    except Exception as e:
        print(f"TikTok API error: {e}")
    
    return None


@app.route('/api/tiktok/download', methods=['GET', 'POST'])
def tiktok_download():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:
        url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required', 'success': False}), 400
    
    try:
        api_result = download_tiktok_via_api(url)
        if api_result and api_result.get('video_url'):
            video_response = requests.get(api_result['video_url'], headers=TIKTOK_HEADERS, timeout=60, stream=True)
            if video_response.status_code == 200:
                temp_dir = tempfile.mkdtemp()
                unique_id = str(uuid.uuid4())[:8]
                video_path = os.path.join(temp_dir, f'tiktok_{unique_id}.mp4')
                
                with open(video_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                title = api_result.get('title', 'tiktok_video')[:50]
                safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:40] or 'tiktok_video'
                return send_file(
                    video_path,
                    as_attachment=True,
                    download_name=f'{safe_title}.mp4',
                    mimetype='video/mp4'
                )
        
        temp_dir = tempfile.mkdtemp()
        unique_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(temp_dir, f'tiktok_{unique_id}.%(ext)s')
        
        options = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': output_path,
            'nocheckcertificate': True,
            'http_headers': TIKTOK_HEADERS,
            'format': 'best',
            'socket_timeout': 30,
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'tiktok_video')
            ext = info.get('ext', 'mp4')
        
        for file in os.listdir(temp_dir):
            if file.startswith(f'tiktok_{unique_id}'):
                return send_file(
                    os.path.join(temp_dir, file),
                    as_attachment=True,
                    download_name=f'{title[:50]}.{ext}',
                    mimetype='video/mp4'
                )
        
        return jsonify({'error': 'Video file not found', 'success': False}), 500
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/tiktok/info', methods=['GET', 'POST'])
def tiktok_info():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:
        url = request.args.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required', 'success': False}), 400
    
    try:
        api_result = download_tiktok_via_api(url)
        if api_result and api_result.get('success'):
            return jsonify({
                'success': True,
                'title': api_result.get('title'),
                'duration': api_result.get('duration'),
                'thumbnail': api_result.get('thumbnail'),
                'uploader': api_result.get('author'),
            })
        
        options = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'http_headers': TIKTOK_HEADERS,
            'socket_timeout': 30,
        }
        
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        
        return jsonify({
            'success': True,
            'title': info.get('title'),
            'duration': info.get('duration'),
            'thumbnail': info.get('thumbnail'),
            'description': info.get('description', '')[:500],
            'uploader': info.get('uploader'),
            'view_count': info.get('view_count'),
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'API is running'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
