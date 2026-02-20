import json
import chromadb
from chromadb.utils import embedding_functions

def load_logs(file_path="logs.json"):
    print(f"Loading logs from {file_path}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Please run main.py first to generate logs.")
        return []

def configure_chroma():
    print("Initializing ChromaDB Client...")
    # Setup local persistent storage for vectors
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Use default sentence-transformers model (all-MiniLM-L6-v2)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Create or get the collection
    collection = chroma_client.get_or_create_collection(
        name="mas_cyber_logs",
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )
    return collection

def insert_logs_to_vectordb(collection, logs):
    if not logs:
        return
        
    print(f"Vectorizing {len(logs)} logs into ChromaDB...")
    
    documents = []
    metadatas = []
    ids = []
    
    for i, log in enumerate(logs):
        # We want the vector search to index the details and action context
        text_representation = f"[{log['event_type'].upper()}] Agent {log['agent']}({log['role']}) performed {log['action']}: {log['details']}"
        documents.append(text_representation)
        
        # Metadata allows for exact-match filtering alongside vector search
        metadatas.append({
            "agent": log["agent"],
            "role": log["role"],
            "action": log["action"],
            "event_type": log["event_type"],
            "timestamp": log["timestamp"]
        })
        
        ids.append(f"log_{i}")
        
    # Batch add to avoid memory issues on huge datasets
    batch_size = 500
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        collection.upsert(
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx],
            ids=ids[i:end_idx]
        )
    
    print("Vectorization complete.")

def query_threat_intel(collection, query_text, n_results=5):
    print(f"\n[RAG SEARCH] Query: '{query_text}'")
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        print("No heavily matching context found in local logs.")
        return
        
    print("\n--- TOP MATCHES IN MAS LOGS ---")
    for i, doc in enumerate(results['documents'][0]):
        distance = results['distances'][0][i] if 'distances' in results else "N/A"
        meta = results['metadatas'][0][i]
        
        # Distance (0 = perfect match, >1 = dissimilar)
        print(f"Match #{i+1} (Dist: {distance:.4f})")
        print(f"  Time: {meta['timestamp']}")
        print(f"  Content: {doc}")
        print("-" * 40)

def main():
    # 1. Load the generated JSON logs
    logs = load_logs()
    if not logs:
        return
        
    # 2. Setup ChromaDB and Embedding model
    collection = configure_chroma()
    
    # 3. Vectorize logs (Upsert avoids duplicates via IDs)
    insert_logs_to_vectordb(collection, logs)
    
    # 4. Perform an example RAG Query
    test_query = "ransomware LATAM TTPs"
    query_threat_intel(collection, test_query)
    
    # Additional test query based on generated Attack patterns
    test_query2 = "port scanning by attacker"
    query_threat_intel(collection, test_query2)

if __name__ == "__main__":
    main()
