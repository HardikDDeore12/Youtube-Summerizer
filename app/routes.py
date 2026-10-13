import os
from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from app.services.transcriber import TranscriberService
from app.services.summarizer import SummarizerService
from app.services.rag_store import RAGStoreService

main_bp = Blueprint('main', __name__)

# Initialize services
transcriber = TranscriberService(model_name="tiny")
summarizer = SummarizerService()
rag_store = RAGStoreService()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/api/process', methods=['POST'])
def process_meeting():
    """Handles YouTube URL or audio file ingestion, transcription, RAG indexing, and local summarization."""
    try:
        meeting_id = request.form.get('meeting_id', 'default_meeting')
        youtube_url = request.form.get('youtube_url')
        audio_file = request.files.get('audio_file')

        audio_path = None

        if youtube_url:
            audio_path = transcriber.download_youtube_audio(youtube_url)
        elif audio_file:
            os.makedirs("data/audio", exist_ok=True)
            filename = secure_filename(audio_file.filename)
            audio_path = os.path.join("data/audio", filename)
            audio_file.save(audio_path)
        else:
            return jsonify({"error": "No YouTube URL or audio file provided."}), 400

        # 1. Transcribe audio locally using Whisper
        transcription_result = transcriber.transcribe(audio_path)
        full_text = transcription_result["text"]
        segments = transcription_result["segments"]

        # 2. Index transcript segments into ChromaDB for RAG search
        rag_store.add_transcript_to_vectorstore(meeting_id, segments)

        # 3. Generate structured summary locally via Ollama (llama3)
        summary_result = summarizer.summarize(full_text)

        return jsonify({
            "status": "success",
            "meeting_id": meeting_id,
            "summary": summary_result,
            "transcript_preview": full_text[:500] + "..."
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@main_bp.route('/api/chat', methods=['POST'])
def chat_with_meeting():
    """RAG endpoint to query specific meeting transcripts locally."""
    data = request.json or {}
    meeting_id = data.get('meeting_id', 'default_meeting')
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "Query is required."}), 400

    results = rag_store.query_transcript(meeting_id, query, k=3)
    return jsonify({
        "status": "success",
        "query": query,
        "results": results
    })