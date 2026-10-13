import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
import json

load_dotenv()

class YouTubeSummarySchema(BaseModel):
    video_overview: str = Field(description="A comprehensive 3-5 sentence summary of what the video is about.")
    key_takeaways: List[str] = Field(description="Major insights, lessons, or conclusions discussed in the video.")
    core_topics: List[str] = Field(description="Key technical concepts, tools, or subjects covered during the discussion.")

class SummarizerService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing from environment variables or .env file!")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.8-flash"

    def summarize(self, transcript_text: str) -> dict:
        prompt = f"""
        Analyze the following YouTube video transcript and extract a detailed overview, 
        key takeaways, and core topics discussed.
        
        Video Transcript:
        {transcript_text}
        """

        # Retry up to 3 times if server is busy (503 error)
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=YouTubeSummarySchema,
                        temperature=0.2,
                    ),
                )
                return json.loads(response.text)
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if "503" in str(e) and attempt < 2:
                    time.sleep(3) # Wait 3 seconds before retrying
                    continue
                else:
                    if attempt == 2:
                        print("Max retries reached due to server traffic.")
                    break

        return {
            "video_overview": "Server is currently experiencing high demand. Please try clicking 'Summarize Video' again in a moment.",
            "key_takeaways": [],
            "core_topics": []
        }