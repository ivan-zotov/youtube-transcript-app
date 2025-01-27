from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    try:
        url = request.form['url']
        video_id = url.split('v=')[1].split('&')[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
        text = ' '.join([entry['text'] for entry in transcript])
        return jsonify({'text': text, 'error': None})
    except Exception as e:
        return jsonify({'text': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)