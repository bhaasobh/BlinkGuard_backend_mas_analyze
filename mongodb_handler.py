import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.blinkguard  # Database name
collection = db.phishing_messages  # Collection name

async def save_phishing_message(message: str, analysis_result: dict = None):
    """
    Saves a message and its analysis result to MongoDB.
    """
    try:
        phishing_doc = {
            "message": message,
            "analysis_result": analysis_result,
            "timestamp": datetime.utcnow()
        }
        await collection.insert_one(phishing_doc)
        print(f"DEBUG: Saved phishing message to MongoDB")
        return True
    except Exception as e:
        print(f"ERROR: Failed to save to MongoDB: {e}")
        return False
