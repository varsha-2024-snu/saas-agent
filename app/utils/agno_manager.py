# app/utils/agno_manager.py
import google.generativeai as genai
from typing import Dict, List, Optional
import logging
import os
from app.config import Config

logger = logging.getLogger(__name__)

class AgnoManager:
    def __init__(self):
        # Direct Gemini configuration
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 2048
            }
        )
        self.tools = self._setup_tools()
        logger.info("AGNO-compatible manager initialized with Gemini")

    def _setup_tools(self) -> List[Dict]:
        """Define tools for the agent"""
        return [
            {
                "name": "search_knowledge_base",
                "description": "Search local Notion documentation",
                "parameters": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer"}
                }
            }
        ]

    async def generate_response(self, user_query: str, context: str = "") -> Dict:
        """Generate response using Gemini with tool awareness"""
        try:
            # Format message with tool specifications
            prompt = f"""
            Available Tools:
            {self._format_tools()}

            Context:
            {context}

            User Query:
            {user_query}

            Respond using markdown and cite sources when available.
            """
            
            response = await self.model.generate_content_async(prompt)
            return {
                "response": response.text,
                "sources": self._extract_sources(response.text),
                "tools_used": []
            }
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            return {
                "response": "I couldn't generate a response. Please try again.",
                "sources": [],
                "tools_used": ["error_handling"]
            }

    def _format_tools(self) -> str:
        """Format tools for the prompt"""
        return "\n".join(
            f"- {tool['name']}: {tool['description']}"
            for tool in self.tools
        )

    def _extract_sources(self, text: str) -> List[str]:
        """Extract sources from response text"""
        # Implement your source extraction logic
        return []