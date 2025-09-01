# rag_service.py
"""
Modular RAG service using LangChain for embedding, retrieval, and LLM answer generation.
"""
# Prefer new adapter packages (langchain-chroma, langchain-ollama) if available.
try:
    from langchain_chroma import Chroma
    from langchain_ollama import OllamaLLM
    from langchain.chains import RetrievalQA
    _ADAPTER = "new"
except Exception:
    # Fallback to langchain_community adapters (older layout)
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.llms import Ollama
        from langchain.chains import RetrievalQA
        _ADAPTER = "legacy"
    except Exception:
        _ADAPTER = None
from banglish_embedding import BanglishBertEmbedder

from config import OLLAMA_MODEL, PERSIST_DIR, COLLECTION_NAME, MODEL_NAME

class _LocalEmbeddingFunction:
    def __init__(self, embedder):
        self.embedder = embedder

    def embed_query(self, text):
        return self.embedder.embed([text])[0].tolist()

    def embed_documents(self, texts):
        embs = self.embedder.embed(texts)
        return [e.tolist() for e in embs]

class RAGService:
    def answer(self, question: str):
        result = self.qa_chain({"query": question})
        answer = result["result"]
        sources = [doc.metadata["source"] for doc in result["source_documents"]]
        return answer, list(set(sources))

    def __init__(self, persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME, model_name=MODEL_NAME, ollama_model=OLLAMA_MODEL):
        if _ADAPTER is None:
            raise RuntimeError(
                "Required LangChain adapter packages are not installed.\n"
                "Install either the new adapter packages:\n"
                "  pip install langchain-chroma langchain-ollama\n"
                "or the legacy community package:\n"
                "  pip install langchain-community\n"
            )
        # Use BanglishBertEmbedder for embeddings
        self.embedder = BanglishBertEmbedder()
        self.embeddings = _LocalEmbeddingFunction(self.embedder)
        # Create Chroma vectorstore (adapter API is consistent for our usage)
        self.vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name=collection_name
        )
        # Create Ollama LLM instance: use new adapter class name if present
        if _ADAPTER == "new":
            self.llm = OllamaLLM(model=ollama_model)
        else:
            self.llm = Ollama(model=ollama_model)

            def __init__(self, persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME, model_name=MODEL_NAME, ollama_model=OLLAMA_MODEL):
                if _ADAPTER is None:
                    raise RuntimeError(
                        "Required LangChain adapter packages are not installed.\n"
                        "Install either the new adapter packages:\n"
                        "  pip install langchain-chroma langchain-ollama\n"
                        "or the legacy community package:\n"
                        "  pip install langchain-community\n"
                    )
            # Use BanglishBertEmbedder for embeddings
            self.embedder = BanglishBertEmbedder()

            class LocalEmbeddingFunction:
                def __init__(self, embedder):
                    self.embedder = embedder

                def embed_query(self, text):
                    return self.embedder.embed([text])[0].tolist()

                def embed_documents(self, texts):
                    embs = self.embedder.embed(texts)
                    return [e.tolist() for e in embs]

            self.embeddings = LocalEmbeddingFunction(self.embedder)
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name=collection_name
            )
            # Create Ollama LLM instance: use new adapter class name if present
            if _ADAPTER == "new":
                self.llm = OllamaLLM(model=ollama_model)
            else:
                self.llm = Ollama(model=ollama_model)
            from langchain.prompts import PromptTemplate
            # General prompt for any company info question
            template = (
                "You are a helpful assistant for a broadband company. Answer the user's question using ONLY the information from the context below. "
                "Ensure the answer is in the same language as the question. "
                "If the answer is present in the context, provide a clear, concise, and direct answer. "
                "If the answer is not in the context, reply: 'Sorry, I couldn't find information about that.'\n"
                "\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
            )
            prompt = PromptTemplate(
                template=template,
                input_variables=["context", "question"]
            )

            # Improved retriever logic for better semantic relevance
            # Extract documents from Chroma
            chroma_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 1000})
            all_documents = chroma_retriever.get_relevant_documents("")  # Retrieve all documents

            # Rebuild FAISS vectorstore
            from langchain.vectorstores import FAISS
            from langchain.embeddings import HuggingFaceEmbeddings

            hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.vectorstore = FAISS.from_documents(all_documents, hf_embeddings)

            # Create a new retriever
            base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

            # Patch qa_chain to use updated retriever
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=base_retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )

            # Update answer method to use base retriever
            def answer_with_base_retriever(question: str):
                # Log semantic search results
                docs = base_retriever.get_relevant_documents(question)
                print("\n[Semantic Search Results]")
                for i, doc in enumerate(docs):
                    print(f"{i + 1}. Source: {doc.metadata['source']}")
                    print(f"   Content: {doc.page_content[:200]}...")  # Print first 200 characters

                result = self.qa_chain.invoke({"query": question})
                answer = result["result"]
                sources = [doc.metadata["source"] for doc in result["source_documents"]]
                return answer, list(set(sources))

            self.answer = answer_with_base_retriever
