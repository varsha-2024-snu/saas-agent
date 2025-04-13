import os
from datetime import datetime
from pypdf import PdfReader
from typing import List, Dict, Optional  # Added missing imports
import logging
from app.utils.local_vector_db import vector_db  # Make sure this uses the SQLite version

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngestor:
    def __init__(self):
        self.chunk_size = 1000  # characters
        self.chunk_overlap = 200

    def process_file(self, file_path: str) -> Optional[List[Dict]]:  # Fixed type hint
        """Process a file into chunks"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)
            
            # Read file content
            if file_ext == '.pdf':
                content = self._read_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            if not content or len(content) < 50:
                logger.warning(f"Skipping {file_name} - empty or too small")
                return None
                
            # Split into chunks
            chunks = self._chunk_text(content)
            
            # Prepare documents for DB
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"{file_name}-{i}",
                    'text': chunk,
                    'metadata': {
                        'source': file_path,
                        'chunk_num': i,
                        'file_type': file_ext[1:],
                        'processed_at': datetime.now().isoformat()
                    }
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None

    def _read_pdf(self, path: str) -> str:
        """Extract text from PDF"""
        try:
            text = ""
            with open(path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"{page_text}\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF read failed: {str(e)}")
            return ""

    def _chunk_text(self, text: str) -> List[str]:  # Now properly typed
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks

    def ingest_directory(self, directory: str):
        """Process all files in directory"""
        logger.info(f"Starting ingestion of {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith('.'):  # Skip hidden files
                    continue
                    
                file_path = os.path.join(root, file)
                documents = self.process_file(file_path)
                
                if documents:
                    if vector_db.upsert_documents(documents):  # Using our SQLite vector_db
                        logger.info(f"Processed {file} → {len(documents)} chunks")
                    else:
                        logger.error(f"Failed to store {file}")
        
        vector_db.close()
        logger.info("Ingestion complete")

if __name__ == "__main__":
    # Create data directory if needed
    os.makedirs("app/data", exist_ok=True)
    
    ingestor = DocumentIngestor()
    ingestor.ingest_directory("app/knowledge")  # Your docs directory