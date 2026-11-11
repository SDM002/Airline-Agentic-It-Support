"""RAG retrieval: Pinecone vector search for candidates, then rerank to keep the most relevant sections."""

from app.config.settings import settings
from app.db.vector_store import reranker, vector_store


# Top RAG_TOP_K by similarity, reranked down to the best RAG_TOP_N, with source, section, score and text
async def search(query: str, category: str | None = None) -> list[dict]:
    text = f"{category}: {query}" if category else query

    candidates = await vector_store.asimilarity_search(text, k=settings.RAG_TOP_K)
    best = await reranker.acompress_documents(candidates, text)

    return [
        {
            "source": d.metadata["source"],
            "section": d.metadata.get("sop") or d.metadata.get("section"),
            "score": round(d.metadata["relevance_score"], 3),
            "text": d.page_content,
        }
        for d in best
    ]
