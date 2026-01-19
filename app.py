from flask import Flask, request, jsonify, send_file, render_template, after_this_request
import requests
import os
import tempfile
import uuid
import shutil
import subprocess
import re

app = Flask(__name__)

def run_node_downloader(url, type, output_path):
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        result = subprocess.run(
            ['node', 'downloader.js', url, type, output_path],
            capture_output=True,
            text=True,
            timeout=300
        )
        print("Stdout:", result.stdout)
        print("Stderr:", result.stderr)
        
        # Extract title from stdout
        title = "downloaded_file"
        title_match = re.search(r'TITLE_START\|(.*?)\|TITLE_END', result.stdout)
        if title_match:
            title = title_match.group(1)
            
        if "Success" in result.stdout:
            return True, None, title
        return False, result.stderr or result.stdout, title
    except Exception as e:
        return False, str(e), "file"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/youtube')
def youtube_page():
    return render_template('youtube.html')

@app.route('/tiktok')
def tiktok_page():
    return render_template('tiktok.html')

@app.route('/api-docs')
def api_docs():
    return render_template('api.html')

@app.route('/api/info')
def get_info():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    
    # Simple YouTube Info extractor using yt-dlp
    try:
        # Check if it's a shorts URL and normalize it
        normalized_url = url
        if 'youtube.com/shorts/' in url:
            video_id = url.split('/shorts/')[1].split('?')[0]
            normalized_url = f"https://www.youtube.com/watch?v={video_id}"

        # YouTube Cookies (Hardcoded)
        COOKIES = "__Secure-1PSIDTS=sidts-CjUB7I_69FxHW2QCiA4MxMN3cOdtRC92m5e79NG729hrvN-u7yf2XHnEUj6EMclRyCa2ny1AdBAA; __Secure-3PSIDTS=sidts-CjUB7I_69FxHW2QCiA4MxMN3cOdtRC92m5e79NG729hrvN-u7yf2XHnEUj6EMclRyCa2ny1AdBAA; HSID=Axvvi7FadBeeCoEkp; SSID=As1unpmenzygkSXVV; APISID=59zjzUgQktgx33dq/AAOi3y4BYyIC72S-6; SAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; __Secure-1PAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; __Secure-3PAPISID=LiKWq-8gQME3PYNf/A0xqExwiRrW7Gl1oi; SID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwl8a1NBOcm4e0OIHjQupXegACgYKAX0SARESFQHGX2MiNz_hpzfNW07XmFPfSEZJJxoVAUF8yKp-UkljsQgpIq__3lRC_6jH0076; __Secure-1PSID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwzgIGckwk68KATq2EJ93fqgACgYKAQwSARESFQHGX2MiouSgqy9S8yGfvSY5GTyDlBoVAUF8yKo77IK6heNTP55gviNrP4dC0076; __Secure-3PSID=g.a0005wjQsplZsjkxOo5-mAeXeKE0W1wyrgl3mGjjVkRp9zcJQYLwhnWLSc3DBpeVigBTfQ5HCgACgYKAV8SARESFQHGX2Miv0afKeDsv9PLSPy8dnoimhoVAUF8yKrhh4xLrzl_FfKuJhCAH1xK0076; __Secure-YNID=15.YT=VzqodTPSls3c8rbOYwmoHXYUq3V9lQjo5ipqIkk5A8rDsPkLQDGvVHRs7gmsZRl99CKkPpLIJMkBTi_9iEXjGOrN-3YcqwvOcRVfpvdyTpes69t-THuRf4Lg9WpG7VUbHVDQSoddQq4ilWb68mICAr849urd8UmB1A9PmOKfYf2pQ6iFjF64yhcYYGLAd4A2lb3OFCS1zeY4YKp3DSWNwYTnBpLb4KxM6IKKoz9-HVOUPigE0CHwnBr_4VNQupKHsIIsbkg3eaojpfUNNw8OpbipzKAGR78kaFMgeZ592OvpuJSF2NRfyHpTLSlxdpqkylkNwPgiJ876N_wQjFaWlA; YSC=NPJ_EOYiux4; VISITOR_INFO1_LIVE=7YzMqpAepms; VISITOR_PRIVACY_METADATA=CgJQSxIEGgAgZQ%3D%3D; PREF=f6=40000000&tz=Asia.Karachi; __Secure-ROLLOUT_TOKEN=CO3Ox7-pgp5wEIb97eull5IDGLjMneiyl5ID; SIDCC=AKEyXzWPrlZBPKS77oNwZqRp0MOT6bYrmketWOYSPs-8Y-GbBpRmtLYisbs9a-NvUWOlri8CEg; __Secure-1PSIDCC=AKEyXzUSUizLeWAOaCjXu0Xbul72VnA9ins55qofiVQArOb2ZKM4IL03qwQIIV5f3tz-U2J88w; __Secure-3PSIDCC=AKEyXzUVF8x5Wtulgmgwj4jXkNrCoGlquYHagIwXCLvanwfzchwUxQzRzZVWjHjuZuUmtBjm"

        result = subprocess.run(
            ['python3', '-m', 'yt_dlp', '--add-header', f"Cookie:{COOKIES}", '--dump-json', '--no-playlist', '--no-check-certificate', normalized_url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            thumbnail = data.get('thumbnail')
            # If thumbnail is a .webp or has issues, we can try to get the maxresdefault
            video_id = data.get('id')
            if video_id and (not thumbnail or '.webp' in thumbnail):
                thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            
            return jsonify({
                'title': data.get('title'),
                'thumbnail': thumbnail,
                'duration': data.get('duration_string')
            })
        else:
            print(f"yt-dlp error: {result.stderr}")
    except Exception as e:
        print(f"Info Error: {e}")
        
    # TikTok Fallback
    if 'tiktok' in url:
        try:
            data = requests.get(f"https://tikwm.com/api/?url={url}").json()
            if data.get('code') == 0:
                return jsonify({
                    'title': data['data'].get('title'),
                    'thumbnail': data['data'].get('cover'),
                    'duration': ''
                })
        except: pass
        
    return jsonify({'title': 'Unknown Media', 'thumbnail': '', 'duration': ''})

@app.route('/api/youtube/audio')
def youtube_audio():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    temp_dir = tempfile.mkdtemp()
    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(temp_dir, f'audio_{unique_id}.mp3')
    
    success, error, title = run_node_downloader(url, 'audio', output_path)
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response
        return send_file(output_path, as_attachment=True, download_name=f"{title}.mp3", mimetype='audio/mpeg')
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    return jsonify({'error': f"Download failed: {error}"}), 500

@app.route('/api/youtube/video')
def youtube_video():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    temp_dir = tempfile.mkdtemp()
    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(temp_dir, f'video_{unique_id}.mp4')
    
    success, error, title = run_node_downloader(url, 'video', output_path)
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response
        return send_file(output_path, as_attachment=True, download_name=f"{title}.mp4", mimetype='video/mp4')
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    return jsonify({'error': f"Download failed: {error}"}), 500

@app.route('/api/tiktok/download')
def tiktok_download():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    try:
        data = requests.get(f"https://tikwm.com/api/?url={url}").json()
        if data.get('code') == 0:
            video_url = data['data']['play']
            title = data['data'].get('title', 'tiktok_video')
            clean_title = re.sub(r'[^\w\s-]', '', title)[:50].strip() or "tiktok"
            video_res = requests.get(video_url, stream=True)
            temp_dir = tempfile.mkdtemp()
            video_path = os.path.join(temp_dir, "video.mp4")
            with open(video_path, 'wb') as f:
                for chunk in video_res.iter_content(chunk_size=8192): f.write(chunk)
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                return response
            return send_file(video_path, as_attachment=True, download_name=f"{clean_title}.mp4", mimetype='video/mp4')
        return jsonify({'error': 'API error'}), 500
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/api/tiktok/audio')
def tiktok_audio():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    try:
        data = requests.get(f"https://tikwm.com/api/?url={url}").json()
        if data.get('code') == 0:
            audio_url = data['data']['music']
            title = data['data'].get('title', 'tiktok_audio')
            clean_title = re.sub(r'[^\w\s-]', '', title)[:50].strip() or "tiktok_audio"
            audio_res = requests.get(audio_url, stream=True)
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, "audio.mp3")
            with open(audio_path, 'wb') as f:
                for chunk in audio_res.iter_content(chunk_size=8192): f.write(chunk)
            @after_this_request
            def cleanup(response):
                shutil.rmtree(temp_dir, ignore_errors=True)
                return response
            return send_file(audio_path, as_attachment=True, download_name=f"{clean_title}.mp3", mimetype='audio/mpeg')
        return jsonify({'error': 'API error'}), 500
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
