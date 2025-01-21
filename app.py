from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
import yt_dlp
import os

app = Flask(__name__, static_folder='static')

# Configuration des headers pour simuler Chrome
CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data['url']
        format = data['type']
        quality = data.get('quality', 'best')

        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]' if format == 'video' else 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'http_headers': CHROME_HEADERS,  # Ajout des headers Chrome
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
            'force_generic_extractor': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return jsonify({
            'file_url': f'/downloads/{os.path.basename(filename)}',
            'filename': os.path.basename(filename)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True) 