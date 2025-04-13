# app/utils/memory_manager.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os
from app.config import Config
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        self.db_path = os.path.join(Config.DATA_DIR, "memory_db.sqlite")
        self.conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id TEXT PRIMARY KEY,
            question TEXT,
            answer TEXT,
            sources TEXT,
            usage_count INTEGER DEFAULT 1,
            last_used TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP
        )
        """)
        self.conn.commit()

    def store_faq(self, question: str, answer: str, sources: List[str]):
        """Store a new FAQ entry"""
        faq_id = f"faq_{hash(question)}"
        try:
            self.conn.execute("""
            INSERT OR REPLACE INTO faqs 
            (id, question, answer, sources, last_used)
            VALUES (?, ?, ?, ?, ?)
            """, (
                faq_id,
                question,
                answer,
                json.dumps(sources),
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to store FAQ: {str(e)}")

    def get_relevant_faqs(self, query: str, threshold: float = 0.85) -> List[Dict]:
        """Retrieve relevant FAQs using simple text matching"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT id, question, answer, sources, usage_count
            FROM faqs
            WHERE question LIKE ? OR answer LIKE ?
            """, (f"%{query}%", f"%{query}%"))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "question": row[1],
                    "answer": row[2],
                    "sources": json.loads(row[3]),
                    "score": 0.9  # Simple matching score
                })
            
            return [r for r in results if r["score"] >= threshold]
        except Exception as e:
            logger.error(f"FAQ retrieval failed: {str(e)}")
            return []

    def increment_faq_counter(self, faq_id: str):
        """Track FAQ usage"""
        try:
            self.conn.execute("""
            UPDATE faqs 
            SET usage_count = usage_count + 1,
                last_used = ?
            WHERE id = ?
            """, (datetime.now().isoformat(), faq_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update FAQ counter: {str(e)}")

    def get_user_context(self, session_id: str) -> Optional[Dict]:
        """Get session-specific context"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            SELECT context FROM sessions WHERE session_id = ?
            """, (session_id,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return None

    def update_user_context(self, session_id: str, interaction: Dict):
        """Update or create session context"""
        try:
            current_context = self.get_user_context(session_id) or {}
            current_context.setdefault("history", []).append(interaction)
            
            self.conn.execute("""
            INSERT OR REPLACE INTO sessions 
            (session_id, context, last_accessed)
            VALUES (?, ?, ?)
            """, (
                session_id,
                json.dumps(current_context),
                datetime.now().isoformat()
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Context update failed: {str(e)}")

    def clear_session_data(self, session_id: str):
        """Remove session-specific data"""
        try:
            self.conn.execute("""
            DELETE FROM sessions WHERE session_id = ?
            """, (session_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Session clear failed: {str(e)}")

    def __del__(self):
        self.conn.close()