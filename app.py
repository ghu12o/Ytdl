from flask import Flask, request, jsonify
from pytube import YouTube
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return "i am ok"
    
@app.route('/get_streams_and_links', methods=['POST'])
def get_streams_and_links():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        # Create a YouTube object from the video URL
        yt = YouTube(video_url)

        # Get all available streams
        streams = yt.streams.all()

        # Create a dictionary to store stream information
        stream_data = {
            "title": yt.title,
            "streams": []
        }

        # Extract information from each stream and add it to the dictionary
        for stream in streams:
            stream_data["streams"].append({
                "resolution": stream.resolution,
                "progressive": stream.is_progressive,
                "itag": stream.itag,
                "url": stream.url,  # Adding stream URL
                "thumbnail_url": yt.thumbnail_url
            })

        return jsonify(stream_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
