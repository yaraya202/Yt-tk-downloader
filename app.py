from flask import Flask, request, jsonify, send_file, render_template, after_this_request
import yt_dlp
import requests
import re
import os
import tempfile
import uuid
import shutil

app = Flask(__name__)

# Hardcoded fresh cookies
YOUTUBE_COOKIES = "__Secure-1PSIDTS=sidts-CjUB7I_69FxHW2QCiA4MxMN3cOdtRC92m5e79NG729hrvN-u7yf2XHnEUj6EMclRyCa2ny1AdBAA; __Secure-3PSIDTS=sidts-CjUB7I_69FxHW2QCiA4MxMN3cOdtRC92m5e79NG729hrvN-u7yf2XHnEUj6EMclRyCa2ny1AdBAA; HSID=Axvvi7FadBeeCoEkp; SSID=As1unpmenzygkSXVV; APISID=59zjzUgQktgx33dq/AAOi3y4BYyIC72S-6; SAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; __Secure-1PAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; __Secure-3PAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; SID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwl8a1NBOcm4e0OIHjQupXegACgYKAX0SARESFQHGX2MiNz_hpzfNW07XmFPfSEZJJxoVAUF8yKp-UkljsQgpIq__3lRC_6jH0076; __Secure-1PSID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwzgIGckwk68KATq2EJ93fqgACgYKAQwSARESFQHGX2MiouSgqy9S8yGfvSY5GTyDlBoVAUF8yKo77IK6heNTP55gviNrP4dC0076; __Secure-3PSID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwhnWLSc3DBpeVigBTfQ5HCgACgYKAV8SARESFQHGX2Miv0afKeDsv9PLSPy8dnoimhoVAUF8yKrhh4xLrzl_FfKuJhCAH1xK0076; __Secure-YNID=15.YT=VzqodTPSls3c8rbOYwmoHXYUq3V9lQjo5ipqIkk5A8rDsPkLQDGvVHRs7gmsZRl99CKkPpLIJMkBTi_9iEXjGOrN-3YcqwvOcRVfpvdyTpes69t-THuRf4Lg9WpG7VUbHVDQSoddQq4ilWb68mICAr849urd8UmB1A9PmOKfYf2pQ6iFjF64yhcYYGLAd4A2lb3OFCS1zeY4YKp3DSWNwYTnBpLb4KxM6IKKoz9-HVOUPigE0CHwnBr_4VNQupKHsIIsbkg3eaojpfUNNw8OpbipzKAGR78kaFMgeZ592OvpuJSF2NRfyHpTLSlxdpqkylkNwPgiJ876N_wQjFaWlA; YSC=NPJ_EOYiux4; __Secure-ROLLOUT_TOKEN=CO3Ox7-pgp5wEIb97eull5IDGIb97eull5ID; VISITOR_INFO1_LIVE=7YzMqpAepms; VISITOR_PRIVACY_METADATA=CgJQSxIEGgAgZQ%3D%3D; PREF=f6=40000000&tz=Asia.Karachi&f7=100; SIDCC=AKEyXzXQxXusP9rqyMwA1JeNVGdnIKvJkp7DEMH-vP-xAJqpA4yj9EW-_KpjPXCBvzXF2cOYZA; __Secure-1PSIDCC=AKEyXzV2Poua5qSYvGa1ODkLMljUr0Zh1CA3d_4V1IkYx8H25V31O8cOrSrZd8pEOGzmv2iJHA; __Secure-3PSIDCC=AKEyXzWsm2eM6TPPFzP9NEDtY5F0BG5cIU7o-R43bCs_13CLoVCBcOFckI42x13SRB6ayK2I"

def create_cookie_file():
    cookie_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    cookie_file.write("# Netscape HTTP Cookie File\n")
    cookie_file.write("# https://curl.haxx.se/rfc/cookie_spec.html\n\n")
    cookies = YOUTUBE_COOKIES.split('; ')
    for cookie in cookies:
        if '=' in cookie:
            parts = cookie.split('=', 1)
            cookie_file.write(f".youtube.com\tTRUE\t/\tTRUE\t2147483647\t{parts[0]}\t{parts[1]}\n")
    cookie_file.close()
    return cookie_file.name

def get_yt_dlp_options(format_type, output_path, quality='best'):
    cookie_file = create_cookie_file()
    base_options = {
        'cookiefile': cookie_file,
        'quiet': True,
        'no_warnings': True,
        'outtmpl': output_path,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nopart': True,
        'no_cache_dir': True,
        'ignoreerrors': True,
        'external_downloader': 'ffmpeg', # Force ffmpeg for better handling
    }
    if format_type == 'audio':
        base_options.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality if quality != 'best' else '128',
            }],
        })
    elif format_type == 'video':
        if quality == '360':
            base_options.update({'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]'})
        elif quality == '720':
            base_options.update({'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]'})
        else:
            base_options.update({'format': 'bestvideo+bestaudio/best'})
        base_options.update({'merge_output_format': 'mp4'})
    return base_options, cookie_file

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/youtube/audio')
def youtube_audio():
    url = request.args.get('url')
    quality = request.args.get('quality', '64')
    if not url: return jsonify({'error': 'URL required'}), 400
    temp_dir = tempfile.mkdtemp()
    try:
        unique_id = uuid.uuid4().hex[:8]
        output_path = os.path.join(temp_dir, f'audio_{unique_id}.%(ext)s')
        options, cookie_file = get_yt_dlp_options('audio', output_path, quality)
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'audio')
        final_file = None
        for f in os.listdir(temp_dir):
            if f.startswith(f'audio_{unique_id}') and f.endswith('.mp3'):
                final_file = os.path.join(temp_dir, f)
                break
        if final_file and os.path.exists(final_file) and os.path.getsize(final_file) > 0:
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                if os.path.exists(cookie_file): os.remove(cookie_file)
                return response
            return send_file(final_file, as_attachment=True, download_name=f"{title}.mp3", mimetype='audio/mpeg')
        raise Exception("Download failed - Check your URL or try again later")
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/youtube/video')
def youtube_video():
    url = request.args.get('url')
    quality = request.args.get('quality', 'best')
    if not url: return jsonify({'error': 'URL required'}), 400
    temp_dir = tempfile.mkdtemp()
    try:
        unique_id = uuid.uuid4().hex[:8]
        output_path = os.path.join(temp_dir, f'video_{unique_id}.%(ext)s')
        options, cookie_file = get_yt_dlp_options('video', output_path, quality)
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
        final_file = None
        for f in os.listdir(temp_dir):
            if f.startswith(f'video_{unique_id}') and f.endswith('.mp4'):
                final_file = os.path.join(temp_dir, f)
                break
        if final_file and os.path.exists(final_file) and os.path.getsize(final_file) > 0:
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                if os.path.exists(cookie_file): os.remove(cookie_file)
                return response
            return send_file(final_file, as_attachment=True, download_name=f"{title}.mp4", mimetype='video/mp4')
        raise Exception("Download failed - Check your URL or try again later")
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/tiktok/download')
def tiktok_download():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    try:
        data = requests.get(f"https://tikwm.com/api/?url={url}").json()
        if data.get('code') == 0:
            video_url = data['data']['play']
            title = data['data'].get('title', 'tiktok')
            video_res = requests.get(video_url, stream=True)
            temp_dir = tempfile.mkdtemp()
            video_path = os.path.join(temp_dir, "video.mp4")
            with open(video_path, 'wb') as f:
                for chunk in video_res.iter_content(chunk_size=8192): f.write(chunk)
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                return response
            return send_file(video_path, as_attachment=True, download_name=f"{title[:50]}.mp4", mimetype='video/mp4')
        return jsonify({'error': 'API error'}), 500
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/health')
def health(): return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
