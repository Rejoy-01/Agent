from typing import Dict
from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("EpisodicMemory", port=8002)  # Unique name and port

DB_PATH = "medical_memory.db"

@mcp.tool()
async def get_episodic_memory(patient_id: str) -> Dict[str, str]:
    """
    Return the most recent visit data for the patient as episodic memory.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, symptoms, diagnosis, prescription
        FROM visits
        WHERE patient_id = ?
        ORDER BY date DESC
        LIMIT 1
    """, (patient_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        date, symptoms, diagnosis, prescription = row
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
    
@mcp.tool()
async def add_episodic_memory(
    patient_id: str,
    visit_date: str,
    symptoms: str,
    diagnosis: str,
    prescription: str
) -> Dict[str, str]:
    """
    Adds a new episodic memory (visit event) to the visits table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO visits (patient_id, date, symptoms, diagnosis, prescription)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, visit_date, symptoms, diagnosis, prescription))

    conn.commit()
    conn.close()

    return {
        "status": "stored",
        "memory_type": "episodic",
        "visit_date": visit_date
    }

if __name__ == "__main__":
    mcp.run(transport="sse")
