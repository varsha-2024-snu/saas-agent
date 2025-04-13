import pinecone
from app.config import Config
from app.utils.embeddings import get_embeddings
from typing import List, Dict
import time

class PineconeDB:
    def __init__(self):
        pinecone.init(api_key=Config.PINECONE_API_KEY)
        
        # Create serverless index if doesn't exist
        if Config.PINECONE_INDEX not in pinecone.list_indexes():
            self._create_serverless_index()
            
        self.index = pinecone.Index(Config.PINECONE_INDEX)
    
    def _create_serverless_index(self):
        """Create a serverless index with retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                pinecone.create_serverless_index(
                    name=Config.PINECONE_INDEX,
                    dimension=768,  # Match your embeddings
                    cloud=Config.PINECONE_CLOUD,
                    region=Config.PINECONE_REGION,
                    metadata_config={"indexed": ["source", "type"]}  # For filtering
                )
                print(f"Serverless index '{Config.PINECONE_INDEX}' created")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to create index after {max_retries} attempts: {str(e)}")
                print(f"Retrying index creation (attempt {attempt + 1})...")
                time.sleep(2 ** attempt)  # Exponential backoff


    def upsert_document(self, doc_id: str, text: str, metadata: dict):
        """Insert or update a document"""
        vector = get_embeddings(text)  # Your embedding function
        self.index.upsert(
            vectors=[(doc_id, vector, metadata)],
            namespace="notion-docs"
        )


    def query(self, query: str, top_k: int = 3, filter: dict = None):
        """Search with optional metadata filtering"""
        query_embedding = get_embeddings(query)
        return self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            namespace="notion-docs",
            include_metadata=True
        )


    def _chunk_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Improved text chunking with overlap"""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - 100):  # 10% overlap
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
    
    # Add these methods to the PineconeDB class
    def upsert_vector(self, vector_id: str, embedding: list, metadata: dict, namespace: str = None):
        self.index.upsert(
            vectors=[(vector_id, embedding, metadata)],
            namespace=namespace
        )

    def query(self, query: str, namespace: str = None, filter: dict = None, top_k: int = 3):
        """Enhanced query with namespace support"""
        query_embedding = get_embeddings(query, task_type="RETRIEVAL_QUERY")
        return self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            filter=filter,
            include_metadata=True
        ).matches