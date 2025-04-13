import logging
from typing import Dict, List, Optional
from datetime import datetime
from app.utils.agno_manager import AgnoManager
from app.utils.local_vector_db import vector_db
from app.utils.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class NotionSupportAgent:
    def __init__(self):
        self.agno = AgnoManager()
        self.memory = MemoryManager()
        logger.info("Notion Support Agent initialized")

    async def query(self, user_query: str, session_id: str = "default") -> Dict:
        """Main query handler"""
        try:
            # 1. Check FAQ memory
            if faq_response := self._check_faq_memory(user_query):
                return {
                    "response": faq_response["answer"],
                    "sources": faq_response["sources"],
                    "is_faq": True,
                    "tools_used": ["faq_retrieval"]
                }

            # 2. Search knowledge base
            context = self._retrieve_knowledge(user_query)
            
            # 3. Generate response
            response = await self.agno.generate_response(
                user_query=user_query,
                context=context
            )

            # 4. Store interaction
            self._store_interaction(
                session_id=session_id,
                question=user_query,
                response=response["response"],
                sources=response["sources"]
            )

            return {
                "response": response["response"],
                "sources": response["sources"],
                "is_faq": False,
                "tools_used": response["tools_used"]
            }

        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return self._error_response()

    def _check_faq_memory(self, query: str) -> Optional[Dict]:
        """Check memory for matching FAQs"""
        faqs = self.memory.get_relevant_faqs(query, threshold=0.9)
        if not faqs:
            return None
            
        best_match = max(faqs, key=lambda x: x['score'])
        self.memory.increment_faq_counter(best_match['id'])
        
        return {
            "answer": best_match['answer'],
            "sources": best_match['sources']
        }

    def _retrieve_knowledge(self, query: str) -> str:
        """Retrieve and format knowledge base results"""
        results = vector_db.search(query, top_k=3)
        return "\n\n".join(
            f"Source: {res['metadata']['source']}\nContent: {res['text']}"
            for res in results
        )

    def _store_interaction(self, session_id: str, question: str, response: str, sources: List[str]):
        """Store conversation in memory"""
        self.memory.update_user_context(
            session_id=session_id,
            interaction={
                "question": question,
                "response": response,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
        )

    def _error_response(self) -> Dict:
        """Generate standardized error response"""
        return {
            "response": "I encountered an error processing your request. Please try again.",
            "sources": [],
            "is_faq": False,
            "tools_used": ["error_handling"]
        }

    def clear_session_memory(self, session_id: str):
        """Clear session-specific data"""
        self.memory.clear_session_data(session_id)
        logger.info(f"Cleared session memory for {session_id}")