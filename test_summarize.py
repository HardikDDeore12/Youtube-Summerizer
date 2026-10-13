import os
from dotenv import load_dotenv
from app.services.summarizer import SummarizerService

# Load environment variables from .env file
load_dotenv()

print("Initializing Summarizer Service...")
try:
    summarizer = SummarizerService()
    
    # Mock meeting transcript
    sample_transcript = """
    Alice: Good morning everyone. Today we need to finalize the launch timeline for our new AI Meeting Assistant.
    Bob: I think we should target the beta release by the end of next month. Charlie, can you handle the backend deployments on Vercel?
    Charlie: Yes, I will set up the Vercel deployment pipeline by next Tuesday.
    Alice: Great. And Hardik will lead the ChromaDB vector search optimization. Let's make sure that's done by Friday.
    Bob: Perfect. So the key decision is to launch the beta next month with local Whisper and Mistral integration.
    """

    print("Running summarization using LangChain LCEL + Mistral...")
    result = summarizer.summarize(sample_transcript)
    
    print("\n--- Structured Summary Result ---")
    import json
    print(json.dumps(result, indent=2))
    print("\nSummarization test passed successfully!")

except Exception as e:
    print(f"Error during summarization test: {e}")
    print("Make sure you have added your MISTRAL_API_KEY to your .env file!")