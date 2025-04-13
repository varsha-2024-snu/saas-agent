from app.agents.notion_agent import NotionSupportAgent
from app.utils.local_vector_db import vector_db  # Our SQLite database
import hashlib
import asyncio
from typing import Dict

def get_session_id(user_id: str) -> str:
    """Create persistent session ID from user identifier"""
    return hashlib.md5(user_id.encode()).hexdigest()

async def main():
    # Initialize components
    agent = NotionSupportAgent()
    
    # User session setup
    user_id = input("Enter your user ID (or 'anonymous'): ").strip()
    session_id = get_session_id(user_id if user_id else "anonymous")
    
    print("\nWelcome to Notion Support Agent! (Type 'quit' to exit)")
    print("-----------------------------------------------")
    
    while True:
        try:
            question = input("\nAsk about Notion: ").strip()
            if question.lower() in ('quit', 'exit'):
                break
                
            if not question:
                print("Please enter a valid question.")
                continue
                
            # Get response with session context
            response = await agent.query(question, session_id)
            
            # Format output
            print("\n" + "="*50)
            print(f"🔍 Response:")
            print(response["response"])
            
            if response["sources"]:
                print("\n📚 Sources:")
                for i, source in enumerate(set(response["sources"]), 1):
                    print(f"{i}. {source}")
            print("="*50)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {str(e)}")
            continue

    # Cleanup
    vector_db.close()
    print("Session ended. Database connection closed.")

if __name__ == "__main__":
    asyncio.run(main())