# Notion AI Support Agent 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

An intelligent support agent for Notion that answers questions using Notion's documentation and real-time web data. Built with **Gemini AI** and optimized for cost-efficiency with **SQLite** as a vector store alternative.


## Key Features ✨

- **Notion Documentation Expert** - Trained on official Notion API docs and help articles
- **Budget-Friendly** - Uses SQLite instead of Pinecone for vector storage
- **Self-Learning** - Builds a knowledge base from user interactions
- **Web-Augmented** - Fetches latest info via Serper API when needed
- **One-Click Adaptation** - Can be converted to other SaaS products

## Tech Stack 🛠️

| Component              | Technology                          |
|------------------------|-------------------------------------|
| **Core AI**            | Google Gemini Pro + Embeddings      |
| **Knowledge Storage**  | SQLite (with vector search)         |
| **Web Search**         | Serper API                          |
| **Backend**            | FastAPI (ready for production)      |
| **Frontend (Future)**  | Streamlit/React                     |

## Installation 💻

```bash
# Clone the repository
git clone https://github.com/yourusername/notion-support-agent.git
cd notion-support-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
