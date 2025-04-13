# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    # Gemini settings
    GENERATION_CONFIG = {
        "temperature": 0.3,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 2048,
    }







    
    