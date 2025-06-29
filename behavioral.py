from typing import Dict
from mcp.server.fastmcp import FastMCP
import sqlite3

mcp = FastMCP("BehavioralMemory", port=8004)

DB_PATH = "behavioral_memory.db"

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS behavior (
            patient_id TEXT PRIMARY KEY,
            missed_appointments INTEGER,
            prefers_teleconsult TEXT,
            habit_notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@mcp.tool()
async def get_behavioral_memory(patient_id: str) -> Dict[str, str]:
    """
    Returns behavioral memory for a patient.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT missed_appointments, prefers_teleconsult, habit_notes
        FROM behavior
        WHERE patient_id = ?
    """, (patient_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        missed, prefers, notes = row
        content = (
            f"Missed appointments: {missed}. "
            f"Prefers teleconsultation: {prefers}. "
            f"Notes: {notes}."
        )
        return {"memory_type": "behavioral", "content": content}
    else:
        return {"memory_type": "behavioral", "content": "No behavioral memory found."}

@mcp.tool()
async def update_behavioral_memory(
    patient_id: str,
    missed_appointments: int,
    prefers_teleconsult: str,
    habit_notes: str
) -> Dict[str, str]:
    """
    Updates or inserts behavioral memory for a patient.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if patient exists
    cursor.execute("SELECT patient_id FROM behavior WHERE patient_id = ?", (patient_id,))
    exists = cursor.fetchone()

    if exists:
        # Update existing record
        cursor.execute("""
            UPDATE behavior
            SET missed_appointments = ?, prefers_teleconsult = ?, habit_notes = ?
            WHERE patient_id = ?
        """, (missed_appointments, prefers_teleconsult, habit_notes, patient_id))
        action = "updated"
    else:
        # Insert new record
        cursor.execute("""
            INSERT INTO behavior (patient_id, missed_appointments, prefers_teleconsult, habit_notes)
            VALUES (?, ?, ?, ?)
        """, (patient_id, missed_appointments, prefers_teleconsult, habit_notes))
        action = "created"

    conn.commit()
    conn.close()

    return {
        "status": action,
        "memory_type": "behavioral",
        "patient_id": patient_id
    }

if __name__ == "__main__":
    mcp.run(transport="sse")
