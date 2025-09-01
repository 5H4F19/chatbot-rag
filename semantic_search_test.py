# semantic_search.py
"""
Given a user question, embed it and search ChromaDB for the most similar company info chunks.
"""
import chromadb
from banglish_embedding import BanglishBertEmbedder


# Import config variables
from config import MODEL_NAME, PERSIST_DIR, COLLECTION_NAME

embedder = BanglishBertEmbedder()
client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)

# 2. Semantic search function
    query_emb = embedder.embed([query])[0]
    # ChromaDB expects a list of queries
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=['documents', 'metadatas']
    )
    hits = []
    # ChromaDB always returns 'ids' in the result, so we can still access them
    for i in range(len(results['ids'][0])):
        hits.append({
            'id': results['ids'][0][i],
            'text': results['documents'][0][i],
            'source': results['metadatas'][0][i]['source']
        })
    return hits

if __name__ == "__main__":
    # Debug: print number of docs in collection
    all_docs = collection.get()
    print(f"Total docs in collection: {len(all_docs['documents'])}")

    user_query = input("Enter your question: ")
    # Debug: print raw results from ChromaDB
    query_emb = model.encode([user_query])[0]
    raw_results = collection.query(
        query_embeddings=[query_emb],
        n_results=3,
        include=['documents', 'metadatas']
    )
    print("Raw ChromaDB results:", raw_results)

    # Use the normal function to print top chunks
    results = search_company_info(user_query)
    print("Top relevant chunks:")
    for hit in results:
        print(f"- Source: {hit['source']}\n  Text: {hit['text']}\n")
