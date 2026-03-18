import os
from typing import List, Dict

from openai import OpenAI
from utils.supabase_store import get_supabase_client


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta la variable de entorno OPENAI_API_KEY.")
    return OpenAI(api_key=api_key)


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


def index_document_in_supabase(document_id: str, full_text: str) -> int:
    supabase = get_supabase_client(use_service_role=True)

    chunks = chunk_text(full_text)
    if not chunks:
        return 0

    embeddings = embed_texts(chunks)

    supabase.table("document_chunks").delete().eq("documento_id", document_id).execute()

    rows = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings), start=1):
        rows.append({
            "documento_id": document_id,
            "chunk_number": idx,
            "contenido": chunk,
            "embedding": emb
        })

    supabase.table("document_chunks").insert(rows).execute()

    return len(chunks)


def semantic_search(query: str, selected_doc_ids: List[str] = None, top_k: int = 8) -> List[Dict]:
    supabase = get_supabase_client(use_service_role=True)

    query_embedding = embed_texts([query])[0]

    result = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": top_k,
            "doc_ids": selected_doc_ids if selected_doc_ids else None
        }
    ).execute()

    rows = result.data or []

    return [
        {
            "id": row["chunk_id"],
            "document_id": row["documento_id"],
            "document_name": row["document_name"],
            "fragment_number": row["chunk_number"],
            "score": round(row["similarity"], 4),
            "hits": [],
            "text": row["contenido"]
        }
        for row in rows
    ]