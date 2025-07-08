from typing import Dict
from fastmcp import FastMCP
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
mcp = FastMCP("EpisodicMemory")

# MongoDB configuration
MONGODB_URI = os.getenv("MongoDB_URI")
DB_NAME = "Medical_Records"
COLLECTION_NAME = "episodic"

def get_mongodb_collection():
    """Get MongoDB collection"""
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]

@mcp.tool()
async def get_episodic_memory(patient_id: str) -> Dict[str, str]:
    """
    Return the most recent visit data for the patient as episodic memory.
    """
    try:
        collection = get_mongodb_collection()

        # Find the most recent visit for the patient
        visit = collection.find_one(
            {"patient_id": patient_id},
            sort=[("date", -1)]
        )

        if visit:
            date = visit.get("date", "Unknown date")
            symptoms = visit.get("symptoms", "No symptoms recorded")
            diagnosis = visit.get("diagnosis", "No diagnosis")
            prescription = visit.get("prescription", "No prescription")

            return {
                "memory_type": "episodic",
                "content": f"On {date}, the patient had {symptoms} and was diagnosed with {diagnosis}. "
                           f"They were treated with {prescription}."
            }
        else:
            return {
                "memory_type": "episodic",
                "content": "No visit history found for this patient."
            }
    except Exception as e:
        return {
            "memory_type": "episodic",
            "content": f"Error retrieving episodic memory: {str(e)}"
        }
    
@mcp.tool()
async def add_episodic_memory(
    patient_id: str,
    date: str,
    symptoms: str,
    diagnosis: str,
    prescription: str
) -> Dict[str, str]:
    """
    Adds a new episodic memory (visit event) to MongoDB.
    Compatible with MCP Client Adapter.
    """
    try:
        collection = get_mongodb_collection()

        # Create visit document
        visit_doc = {
            "patient_id": patient_id,
            "date": date,
            "symptoms": symptoms,
            "diagnosis": diagnosis,
            "prescription": prescription,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        # Insert into MongoDB
        result = collection.insert_one(visit_doc)

        return {
            "success": True,
            "status": "stored",
            "memory_type": "episodic",
            "visit_date": date,
            "document_id": str(result.inserted_id)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "memory_type": "episodic"
        }

# Alias for MCP Client Adapter compatibility
@mcp.tool()
async def episodic_add_visit(
    patient_id: str,
    date: str,
    symptoms: str,
    diagnosis: str,
    prescription: str
) -> Dict[str, str]:
    """
    Alias for add_episodic_memory - used by MCP Client Adapter
    """
    return await add_episodic_memory(patient_id, date, symptoms, diagnosis, prescription)

if __name__ == "__main__":
    mcp.run(transport="stdio", port=8002)
