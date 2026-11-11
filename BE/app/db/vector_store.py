"""Pinecone connection: the index, the hosted embedding model and the hosted reranker."""

from langchain_pinecone import PineconeEmbeddings, PineconeRerank, PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config.settings import settings

api_key = settings.PINECONE_API_KEY.get_secret_value()

pc = Pinecone(api_key=api_key)

# Creates the index on first use; ingest_kb.py fills it
if not pc.has_index(settings.PINECONE_INDEX):
    pc.create_index(
        name=settings.PINECONE_INDEX,
        dimension=settings.PINECONE_EMBED_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION),
    )

embeddings = PineconeEmbeddings(model=settings.PINECONE_EMBED_MODEL, pinecone_api_key=api_key)

vector_store = PineconeVectorStore(index=pc.Index(settings.PINECONE_INDEX), embedding=embeddings)

reranker = PineconeRerank(model=settings.PINECONE_RERANK_MODEL, top_n=settings.RAG_TOP_N, pinecone_api_key=api_key)
