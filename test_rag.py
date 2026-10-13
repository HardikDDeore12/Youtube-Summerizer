from app.services.rag_store import RAGStoreService

print("Initializing RAG Store Service...")
rag = RAGStoreService()

# Mock transcript segments with timestamps
sample_segments = [
    {"start": 0.0, "end": 5.5, "text": "Welcome everyone to the quarterly AI project review meeting."},
    {"start": 5.5, "end": 12.0, "text": "Hardik will lead the ChromaDB vector search and retrieval optimization task."},
    {"start": 12.0, "end": 20.1, "text": "Charlie is responsible for setting up the Vercel deployment pipeline by next Tuesday."}
]

meeting_id = "test_meeting_123"
print(f"Adding transcript segments to ChromaDB for meeting: {meeting_id}...")
rag.add_transcript_to_vectorstore(meeting_id, sample_segments)

print("\nTesting semantic search query: 'Who is handling Vercel?'")
results = rag.query_transcript(meeting_id, "Who is handling Vercel?", k=2)

print("\n--- RAG Search Results ---")
for i, res in enumerate(results, 1):
    print(f"{i}. [{res['timestamp']}] {res['text']}")

print("\nRAG Store test passed successfully!")