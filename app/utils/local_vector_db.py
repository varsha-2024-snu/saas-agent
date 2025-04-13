import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from typing import List, Dict
from app.config import Config

class VectorDB:
    def __init__(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        self.db_path = os.path.join(Config.DATA_DIR, "notion_vector_db.sqlite")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim embeddings
        self.dimension = 384
        
        # Initialize database
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create database tables"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            text TEXT,
            embedding BLOB,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def upsert_documents(self, documents: List[Dict]):
        """Insert or update documents with embeddings"""
        try:
            # Prepare batch data
            ids = [doc['id'] for doc in documents]
            texts = [doc['text'] for doc in documents]
            metadatas = [doc.get('metadata', {}) for doc in documents]
            
            # Generate embeddings
            embeddings = self.embedder.encode(texts)
            
            # Insert in transaction
            self.cursor.executemany("""
            INSERT OR REPLACE INTO documents (id, text, embedding, metadata)
            VALUES (?, ?, ?, ?)
            """, [
                (ids[i], texts[i], embeddings[i].tobytes(), json.dumps(metadatas[i]))
                for i in range(len(ids))
            ])
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error upserting documents: {str(e)}")
            self.conn.rollback()
            return False

    def search(self, query: str, top_k: int = 3, filters: Dict = None) -> List[Dict]:
        """Semantic search with cosine similarity"""
        try:
            # Embed the query
            query_embedding = self.embedder.encode(query)
            
            # Get all documents (filtering not implemented in this simple version)
            self.cursor.execute("SELECT id, text, embedding, metadata FROM documents")
            rows = self.cursor.fetchall()
            
            # Calculate similarities
            results = []
            for row in rows:
                doc_id, text, embedding_bytes, metadata_json = row
                embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                
                # Cosine similarity
                similarity = np.dot(query_embedding, embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(embedding))
                
                results.append({
                    'id': doc_id,
                    'text': text,
                    'metadata': json.loads(metadata_json),
                    'score': float(similarity)
                })
            
            # Sort by score and return top results
            return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []

    def close(self):
        """Close database connection"""
        self.conn.close()

# Global instance
vector_db = VectorDB()