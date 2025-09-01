# check_chromadb.py
"""
Check the contents of the ChromaDB vector database: print number of collections, number of documents in 'company_info', and sample docs.
"""
import chromadb
import os

PERSIST_DIR = 'chromadb_store'
COLLECTION_NAME = 'company_info'

print("Current working directory:", os.getcwd())
print("ChromaDB persist_directory:", PERSIST_DIR)
print("ChromaDB collection name:", COLLECTION_NAME)

client = chromadb.PersistentClient(path=PERSIST_DIR)
collections = client.list_collections()
print(f"Collections in DB: {[c.name for c in collections]}")

if COLLECTION_NAME in [c.name for c in collections]:
    collection = client.get_collection(COLLECTION_NAME)
    all_docs = collection.get()
    print(f"Total docs in '{COLLECTION_NAME}': {len(all_docs['documents'])}")
    print("Sample docs:")
    for i, doc in enumerate(all_docs['documents'][:3]):
        print(f"Doc {i+1}: {doc}")
else:
    print(f"Collection '{COLLECTION_NAME}' not found.")
