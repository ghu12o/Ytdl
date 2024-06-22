from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from pytube import YouTube

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Serve static files (your HTML file)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Endpoint to fetch video qualities
@app.route('/getQualities', methods=['POST'])
def get_qualities():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'Missing video URL'}), 400

    try:
        yt = YouTube(video_url)
        title = yt.title
        
        # Get all streams
        streams = yt.streams

        # Filter video streams (MP4)
        video_formats = []
        for stream in streams.filter(file_extension='mp4'):
            video_formats.append({
                'itag': stream.itag,
                'resolution': stream.resolution,
                'mime_type': stream.mime_type,
                'file_size': stream.filesize,
                'type': 'video'
            })

        # Filter audio streams (MP4 and WebM)
        audio_formats = []
        for stream in streams.filter(type='audio'):
            audio_formats.append({
                'itag': stream.itag,
                'abr': stream.abr,
                'mime_type': stream.mime_type,
                'file_size': stream.filesize,
                'type': 'audio'
            })

        return jsonify({
            'title': title,
            'video_formats': video_formats,
            'audio_formats': audio_formats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to get download URL for a specific quality
@app.route('/getDownloadUrl', methods=['GET'])
def get_download_url():
    video_url = request.args.get('videoUrl')
    itag = request.args.get('itag')

    if not video_url or not itag:
        return jsonify({'error': 'Missing videoUrl or itag parameter'}), 400

    try:
        yt = YouTube(video_url)
        stream = yt.streams.get_by_itag(itag)

        if not stream:
            return jsonify({'error': 'Stream not found'}), 404

        download_url = stream.url
        filename = download_url.split('/')[-1]

        # Prepare response to force download
        response = Response()
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['X-Accel-Redirect'] = download_url
        
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
