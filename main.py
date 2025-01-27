import os
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = Flask(__name__)

def extract_video_id(url):
    """
    Извлекает video_id из различных форматов URL YouTube.
    Поддерживает стандартные и короткие ссылки.
    """
    try:
        if 'v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif '/embed/' in url:
            return url.split('/embed/')[1].split('?')[0]
        else:
            return None
    except IndexError:
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    try:
        url = request.form['url']
        video_id = extract_video_id(url)
        
        if not video_id:
            return jsonify({'text': None, 'error': 'Не удалось извлечь ID видео из предоставленной ссылки.'})
        
        # Попытка получить транскрипт
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
        text = ' '.join([entry['text'] for entry in transcript])
        return jsonify({'text': text, 'error': None})
    
    except TranscriptsDisabled:
        error_message = 'Субтитры отключены для этого видео.'
    except NoTranscriptFound:
        error_message = 'Транскрипт для этого видео не найден на указанных языках (ru, en).'
    except VideoUnavailable:
        error_message = 'Видео недоступно. Проверьте правильность ссылки или попробуйте другое видео.'
    except Exception as e:
        error_message = f'Произошла ошибка: {str(e)}'
    
    return jsonify({'text': None, 'error': error_message})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
