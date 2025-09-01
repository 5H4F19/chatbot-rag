# embed_company_info.py
"""
Reads all .txt files in the company_info folder, splits them into chunks, generates embeddings, and stores them in ChromaDB.
"""
import os
from pathlib import Path
from banglish_embedding import BanglishBertEmbedder
import chromadb
from chromadb.config import Settings

from config import MODEL_NAME, PERSIST_DIR, COLLECTION_NAME

# 1. Read and chunk documents
def read_and_chunk_docs(folder_path, chunk_size=500):
    docs = []
    for file in Path(folder_path).glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read().strip()
            # Treat the entire file content as a single chunk
            docs.append({
                "text": text,
                "source": file.name,
                "language": "bn" if "_bn" in file.name else "en"
            })
    return docs

# 2. Generate embeddings
def embed_chunks(docs):
    embedder = BanglishBertEmbedder()
    texts = [doc['text'] for doc in docs]
    embeddings = embedder.embed(texts)
    return embeddings

# 3. Store in ChromaDB
def store_in_chromadb(docs, embeddings, persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME):
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(collection_name)
    for i, doc in enumerate(docs):
        emb = None
        try:
            emb = embeddings[i].tolist()
        except Exception:
            emb = list(embeddings[i])
        collection.add(
            documents=[doc["text"]],
            metadatas=[{
                "source": doc["source"],
                "language": doc["language"]
            }],
            ids=[f"doc_{i}"],
            embeddings=[emb]
        )
    # Persistence is automatic with persist_directory
    print(f"Stored {len(docs)} chunks in ChromaDB.")

if __name__ == "__main__":
    import subprocess
    print("\n--- Checking ChromaDB BEFORE embedding ---")
    subprocess.run(['python', 'check_chromadb.py'])

    folder = 'company_info'
    print("Reading and chunking documents...")
    docs = read_and_chunk_docs(folder)
    print(f"Total chunks: {len(docs)}")
    print("Generating embeddings...")
    embeddings = embed_chunks(docs)
    print("Storing in ChromaDB...")
    store_in_chromadb(docs, embeddings)
    print("Done.")

    print("\n--- Checking ChromaDB AFTER embedding ---")
    subprocess.run(['python', 'check_chromadb.py'])
