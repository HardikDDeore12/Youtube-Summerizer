import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
import whisper
import yt_dlp

class TranscriberService:
    def __init__(self, model_name="tiny"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy load Whisper model only if fallback is needed."""
        if self._model is None:
            print(f"Loading Whisper model ({self.model_name}) for fallback transcription...")
            self._model = whisper.load_model(self.model_name)
        return self._model

    def extract_video_id(self, url: str) -> str:
        """Extracts YouTube video ID from various URL formats."""
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def download_youtube_audio(self, url: str, output_dir: str = "data/audio") -> str:
        """Downloads audio from YouTube using yt-dlp."""
        os.makedirs(output_dir, exist_ok=True)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            return base + ".mp3"

    def transcribe(self, youtube_url_or_path: str) -> dict:
        """Tries fast YouTube captions first; falls back to Whisper for Hindi/no-caption videos."""
        try:
            video_id = self.extract_video_id(youtube_url_or_path)
            
            # Step 1: Try fetching instant captions (Supports English, Hindi, and auto-captions)
            if video_id:
                try:
                    print(f"Trying instant YouTube captions for ID: {video_id}...")
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en', 'auto'])
                    
                    full_text = " ".join([item['text'] for item in transcript_list])
                    segments = [
                        {
                            "start": item['start'],
                            "end": item['start'] + item.get('duration', 0),
                            "text": item['text']
                        }
                        for item in transcript_list
                    ]
                    print("Successfully fetched via YouTube captions!")
                    return {"text": full_text, "segments": segments}
                    
                except Exception as cap_err:
                    print(f"Captions not available or failed ({cap_err}). Falling back to Whisper audio download...")

            # Step 2: Fallback to Whisper (Handles Hindi audio, custom files, or videos without captions)
            audio_path = self.download_youtube_audio(youtube_url_or_path, "data/audio") if video_id else youtube_url_or_path
            
            print(f"Transcribing audio using Whisper model...")
            result = self.model.transcribe(audio_path)
            
            return {
                "text": result["text"],
                "segments": result.get("segments", [])
            }

        except Exception as e:
            print(f"Error during transcription: {e}")
            return {
                "text": "Transcription failed completely for this video.",
                "segments": []
            }