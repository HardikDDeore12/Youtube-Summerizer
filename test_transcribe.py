from app.services.transcriber import TranscriberService
import os

print('Initializing Transcriber Service...')
# Using tiny model for fast testing
transcriber = TranscriberService(model_name='tiny')

print('Downloading sample YouTube audio...')
# A short public domain / test video URL
sample_url = 'https://www.youtube.com/watch?v=jNQXAC9IVRw' 

try:
    audio_path = transcriber.download_youtube_audio(sample_url)
    print(f'Audio downloaded successfully to: {audio_path}')
    
    print('Running transcription...')
    result = transcriber.transcribe(audio_path)
    print('\n--- Transcription Result ---')
    print(result['text'][:300] + '...')
    print('Transcription test passed successfully!')
except Exception as e:
    print(f'Error during test: {e}')
