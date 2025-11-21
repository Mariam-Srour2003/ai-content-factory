# chroma_manager_hybrid.py
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from langchain_chroma.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from ..config.config_loader import load_config

# Singleton pattern to prevent multiple clients for same path
_client_instances = {}

class VectorStoreHybrid:
    def __init__(self, persist_directory: Optional[Path] = None):
        settings = load_config().vector_db
        self.persist_dir = str(persist_directory or settings.persist_directory)

        if not self.persist_dir:
            raise ValueError("persist_directory cannot be None or empty.")

        # Use singleton pattern for chromadb client
        if self.persist_dir not in _client_instances:
            _client_instances[self.persist_dir] = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )

        self.client = _client_instances[self.persist_dir]

        # LangChain embedding wrapper for retrieval usage
        self.lc_embedding = OllamaEmbeddings(model=settings.embedding_model)

        print(f"✓ Chroma PersistentClient + LangChain adapter initialized at: {self.persist_dir}")

    # example admin method that uses chromadb directly
    def list_collections(self) -> List[str]:
        return [c.name for c in self.client.list_collections()]

    # use LangChain Chroma for adds & queries
    def add_documents(self, collection_name: str, texts: List[str], metadatas: List[Dict[str,Any]], ids: Optional[List[str]] = None):
        vs = Chroma(
            collection_name=collection_name,
            embedding_function=self.lc_embedding,
            client=self.client  # Reuse existing client
        )
        vs.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return len(texts)

    def query(self, collection_name: str, query_text: str, k: int = 5):
        vs = Chroma(
            collection_name=collection_name,
            embedding_function=self.lc_embedding,
            client=self.client  # Reuse existing client
        )
        return vs.similarity_search(query_text, k=k)

    # raw ops still available if needed:
    def delete_collection(self, name: str):
        self.client.delete_collection(name=name)
