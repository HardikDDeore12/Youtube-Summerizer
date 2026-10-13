import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

class RAGStoreService:
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = persist_directory
        # Use a lightweight, high-performance HuggingFace embedding model locally
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        os.makedirs(persist_directory, exist_ok=True)

    def add_transcript_to_vectorstore(self, meeting_id: str, segments: list):
        """
        Takes Whisper transcript segments (with timestamps) and indexes them into ChromaDB.
        """
        documents = []
        for segment in segments:
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            text = segment.get("text", "").strip()
            
            # Format timestamp for readable citation (e.g., [00:01:25])
            time_formatted = f"{int(start // 60):02d}:{int(start % 60):02d}"
            
            doc = Document(
                page_content=text,
                metadata={
                    "meeting_id": meeting_id,
                    "start_time": start,
                    "timestamp": time_formatted,
                    "source_segment": f"[{time_formatted}] {text}"
                }
            )
            documents.append(doc)

        # Initialize Chroma vector store with persistence
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=f"meeting_{meeting_id}"
        )
        return vectorstore

    def query_transcript(self, meeting_id: str, query: str, k: int = 3):
        """
        Searches the ChromaDB vector store for relevant transcript sections matching the query.
        """
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"meeting_{meeting_id}"
        )
        
        results = vectorstore.similarity_search(query, k=k)
        return [
            {
                "text": doc.page_content,
                "timestamp": doc.metadata.get("timestamp"),
                "meeting_id": doc.metadata.get("meeting_id")
            }
            for doc in results
        ]