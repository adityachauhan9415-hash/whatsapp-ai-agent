import chromadb
import hashlib
from sentence_transformers import SentenceTransformer

# Initialize embedding model
EMBEDDING_MODEL = SentenceTransformer('intfloat/multilingual-e5-small')

def generate_unique_id(pair: dict) -> str:
    """Generate a deterministic unique ID for a memory record."""
    stable_fields = f"{pair['relationship']}{pair['contact_name']}{pair['timestamp']}{pair['incoming']}"
    return hashlib.sha256(stable_fields.encode('utf-8')).hexdigest()

# Initialize Chroma client
CHROMA_CLIENT = chromadb.PersistentClient(path="data/chroma")

def generate_embedding(text: str, is_query: bool = False):
    """Generate embedding for given text using the sentence transformer model."""
    prefix = "query: " if is_query else "passage: "
    return EMBEDDING_MODEL.encode(prefix + text).tolist()


def get_chroma_collection(collection_name: str, client=None):
    """Get or create a Chroma collection with the given name."""
    if client is None:
        client = CHROMA_CLIENT
    return client.get_or_create_collection(name=collection_name)


def ingest_memory_pair(pair: dict, client=None):
    """Ingest a memory pair into the appropriate Chroma collection."""
    # Embed only the incoming text as a passage
    embedding = generate_embedding(pair["incoming"], is_query=False)

    # Store in appropriate collection
    collection_name = f"whatsapp_memory_{pair['relationship']}"
    collection = get_chroma_collection(collection_name, client=client)

    unique_id = generate_unique_id(pair)
    collection.upsert(
        ids=[unique_id],
        embeddings=[embedding],
        metadatas=[{
            "timestamp": pair["timestamp"],
            "relationship": pair["relationship"],
            "contact_name": pair["contact_name"],
            "reply": pair["reply"]
        }],
        documents=[pair["incoming"]]
    )


def retrieve_memory(incoming_text: str, relationship: str, n_results: int = 3):
    """Retrieve similar memories from the appropriate Chroma collection."""
    # Embed the new incoming text as a query
    query_embedding = generate_embedding(incoming_text, is_query=True)

    # Query the appropriate collection
    collection_name = f"whatsapp_memory_{relationship}"
    collection = get_chroma_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    # Format results
    formatted_results = []
    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        formatted_results.append({
            "incoming": doc,
            "reply": metadata["reply"],
            "contact_name": metadata["contact_name"],
            "timestamp": metadata["timestamp"],
            "distance": distance
        })

    return formatted_results

# Mock test data
def test_history_brain():
    """Test the history brain implementation with mock data."""
    test_pair = {
        "timestamp": "6/28/26, 10:28:34 AM",
        "relationship": "friend",
        "contact_name": "Prateek",
        "incoming": "Thora mahnga h but sahi h sikhne ke liye",
        "reply": "Ha"
    }

    # Ingest test pair
    ingest_memory_pair(test_pair)

    # Retrieve similar memory
    results = retrieve_memory(
        incoming_text="Mahnga h but sahi h",
        relationship="friend",
        n_results=1
    )

    return results

if __name__ == "__main__":
    # Run mock test
    test_results = test_history_brain()
    print("Test results:", test_results)
