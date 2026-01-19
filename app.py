from flask import Flask, request, jsonify, send_file, render_template, after_this_request
import requests
import os
import tempfile
import uuid
import shutil
import subprocess

app = Flask(__name__)

def run_node_downloader(url, type, output_path):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        result = subprocess.run(
            ['node', 'downloader.js', url, type, output_path],
            capture_output=True,
            text=True,
            timeout=300 # Increased timeout for larger videos
        )
        print("Stdout:", result.stdout)
        print("Stderr:", result.stderr)
        
        if "Success" in result.stdout:
            return True, None
        return False, result.stderr or result.stdout
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/youtube/audio')
def youtube_audio():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    temp_dir = tempfile.mkdtemp()
    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(temp_dir, f'audio_{unique_id}.mp3')
    
    success, error = run_node_downloader(url, 'audio', output_path)
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response
        return send_file(output_path, as_attachment=True, download_name="audio.mp3", mimetype='audio/mpeg')
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    return jsonify({'error': f"Download failed: {error}"}), 500

@app.route('/api/youtube/video')
def youtube_video():
    url = request.args.get('url')
    if not url: return jsonify({'error': 'URL required'}), 400
    temp_dir = tempfile.mkdtemp()
    unique_id = uuid.uuid4().hex[:8]
    output_path = os.path.join(temp_dir, f'video_{unique_id}.mp4')
    
    success, error = run_node_downloader(url, 'video', output_path)
    
    if success and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        @after_this_request
        def cleanup(response):
            shutil.rmtree(temp_dir, ignore_errors=True)
            return response
        return send_file(output_path, as_attachment=True, download_name="video.mp4", mimetype='video/mp4')
    
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
def health():
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
