from typing import Dict
from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import uuid
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
mcp = FastMCP("SemanticMemory", port=8003)
QDRANT_API_KEY = os.getenv("Qdrant_API_KEY")

# Connect to Qdrant cloud instance
QDRANT_URL = "https://c4c84cb4-8c10-42a6-8b30-6b51c73c8757.us-west-1-0.aws.cloud.qdrant.io:6333"

# Initialize components with error handling
def initialize_components():
    """Initialize Qdrant client and sentence transformer with proper error handling."""
    global qdrant_client, encoder

    try:
        # Initialize Qdrant client
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        logger.info("Successfully connected to Qdrant")

        # Initialize sentence transformer with error handling
        try:
            # Try to load the model without authentication first
            os.environ.pop('HF_TOKEN', None)  # Remove any existing token
            encoder = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=False)
            logger.info("Successfully loaded sentence transformer")
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer: {e}")
            logger.info("Trying alternative model...")
            # Fallback to a different model or local model
            try:
                encoder = SentenceTransformer("paraphrase-MiniLM-L6-v2", use_auth_token=False)
                logger.info("Successfully loaded fallback sentence transformer")
            except Exception as e2:
                logger.error(f"Failed to load any sentence transformer: {e2}")
                raise Exception("Could not initialize sentence transformer. Please check your Hugging Face setup.")

    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        raise

# Initialize components
try:
    initialize_components()
except Exception as e:
    logger.error(f"Failed to initialize semantic memory system: {e}")
    # Set fallback values
    qdrant_client = None
    encoder = None

COLLECTION_NAME = "semantic_memory"

# Ensure collection exists
try:
    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Created collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"Error connecting to Qdrant: {e}")

@mcp.tool()
async def add_semantic_memory(patient_id: str, fact: str) -> Dict[str, str]:
    """
    Stores a semantic fact about a patient.
    """
    if not qdrant_client or not encoder:
        return {"status": "error", "memory_type": "semantic", "error": "Semantic memory system not initialized"}

    try:
        embedding = encoder.encode(fact).tolist()
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"patient_id": patient_id, "fact": fact}
        )
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=[point])
        logger.info(f"Stored semantic memory for patient {patient_id}: {fact[:50]}...")
        return {"status": "stored", "memory_type": "semantic", "fact": fact}
    except Exception as e:
        logger.error(f"Error storing semantic memory: {e}")
        return {"status": "error", "memory_type": "semantic", "error": str(e)}

@mcp.tool()
async def get_semantic_memory(patient_id: str, context: str = "") -> Dict[str, str]:
    """
    Retrieves relevant semantic memory chunks for a patient using similarity search.

    Args:
        patient_id: The ID of the patient
        context: Optional context to guide the search (e.g., symptoms or current topic)
    """
    if not qdrant_client or not encoder:
        return {
            "memory_type": "semantic",
            "content": "Semantic memory system not initialized"
        }

    try:
        # Use context if provided, otherwise use default query
        query_text = context if context else f"health information about patient {patient_id}"
        query_vector = encoder.encode(query_text).tolist()

        result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=5,
            query_filter={
                "must": [{"key": "patient_id", "match": {"value": patient_id}}]
            }
        )

        facts = [hit.payload["fact"] for hit in result] if result else []
        logger.info(f"Retrieved {len(facts)} semantic memories for patient {patient_id}")
        return {
            "memory_type": "semantic",
            "content": "\n".join(facts) if facts else "No semantic memory found."
        }
    except Exception as e:
        logger.error(f"Error retrieving semantic memory: {e}")
        return {
            "memory_type": "semantic",
            "content": f"Error retrieving semantic memory: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="sse")
