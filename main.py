import os
import logging
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f'Получен запрос на транскрипт для URL: {url}')
        video_id = extract_video_id(url)
        
        if not video_id:
            logger.error('Не удалось извлечь video_id из URL.')
            return jsonify({'text': None, 'error': 'Не удалось извлечь ID видео из предоставленной ссылки.'})
        
        # Попытка получить транскрипт
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
        text = ' '.join([entry['text'] for entry in transcript])
        logger.info('Транскрипт успешно получен.')
        return jsonify({'text': text, 'error': None})
    
    except TranscriptsDisabled:
        error_message = 'Субтитры отключены для этого видео.'
        logger.warning(f'Субтитры отключены для видео ID: {video_id}')
    except NoTranscriptFound:
        error_message = 'Транскрипт для этого видео не найден на указанных языках (ru, en).'
        logger.warning(f'Транскрипт не найден для видео ID: {video_id}')
    except VideoUnavailable:
        error_message = 'Видео недоступно. Проверьте правильность ссылки или попробуйте другое видео.'
        logger.warning(f'Видео недоступно для видео ID: {video_id}')
    except Exception as e:
        error_message = f'Произошла ошибка: {str(e)}'
        logger.error(f'Неизвестная ошибка для видео ID: {video_id} - {str(e)}')
    
    return jsonify({'text': None, 'error': error_message})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)
