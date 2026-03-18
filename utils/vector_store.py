import os
from typing import List, Dict

import chromadb
from openai import OpenAI

from utils.helpers import ensure_directories

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma")
COLLECTION_NAME = "consultador_docs"


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta la variable de entorno OPENAI_API_KEY.")
    return OpenAI(api_key=api_key)


def get_chroma_client():
    ensure_directories()
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    clean = " ".join((text or "").split())
    if not clean:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(clean):
        end = start + chunk_size
        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


def embed_texts(texts: List[str], model: str = "text-embedding-3-small", batch_size: int = 100) -> List[List[float]]:
    if not texts:
        return []

    client = get_openai_client()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=model,
            input=batch
        )
        all_embeddings.extend([item.embedding for item in response.data])

    return all_embeddings


def remove_document_from_index(document_name: str):
    collection = get_collection()
    try:
        collection.delete(where={"document_name": document_name})
    except Exception:
        pass


def index_document(document_name: str, full_text: str) -> int:
    collection = get_collection()

    # Borra la versión anterior del mismo documento, si existe
    remove_document_from_index(document_name)

    chunks = chunk_text(full_text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    ids = []
    metadatas = []
    documents = []

    for idx, chunk in enumerate(chunks, start=1):
        ids.append(f"{document_name}::chunk::{idx}")
        metadatas.append({
            "document_name": document_name,
            "chunk_number": idx
        })
        documents.append(chunk)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(chunks)


def semantic_search(query: str, selected_docs: List[str] = None, top_k: int = 8) -> List[Dict]:
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed_texts([query])[0]

    raw = collection.query(
        query_embeddings=[query_embedding],
        n_results=max(top_k * 4, 20)
    )

    ids = raw.get("ids", [[]])[0]
    docs = raw.get("documents", [[]])[0]
    metas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]

    results = []
    for item_id, doc_text, meta, distance in zip(ids, docs, metas, distances):
        document_name = meta.get("document_name", "")
        if selected_docs and document_name not in selected_docs:
            continue

        results.append({
            "id": item_id,
            "document_name": document_name,
            "fragment_number": meta.get("chunk_number", 0),
            "score": round(1 / (1 + float(distance)), 4) if distance is not None else 0.0,
            "hits": [],
            "text": doc_text
        })

        if len(results) >= top_k:
            break

    return results


def get_indexed_stats():
    collection = get_collection()
    total_chunks = collection.count()

    if total_chunks == 0:
        return {
            "total_chunks": 0,
            "documents_indexed": 0
        }

    raw = collection.get(include=["metadatas"])
    metadatas = raw.get("metadatas", [])
    document_names = {m.get("document_name") for m in metadatas if m.get("document_name")}

    return {
        "total_chunks": total_chunks,
        "documents_indexed": len(document_names)
    }