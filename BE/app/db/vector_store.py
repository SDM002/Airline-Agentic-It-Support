"""Pinecone connection for RAG: the index, the hosted embedding model and the hosted reranker."""

from langchain_pinecone import PineconeEmbeddings, PineconeRerank, PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config.settings import settings

api_key = settings.PINECONE_API_KEY.get_secret_value()

# Pinecone client
pc = Pinecone(api_key=api_key)

# Create the index on first use; scripts/ingest_kb.py fills it
if not pc.has_index(settings.PINECONE_INDEX):
    pc.create_index(
        name=settings.PINECONE_INDEX,
        dimension=settings.PINECONE_EMBED_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud=settings.PINECONE_CLOUD, region=settings.PINECONE_REGION),
    )

# Hosted model that turns text into vectors
embeddings = PineconeEmbeddings(model=settings.PINECONE_EMBED_MODEL, pinecone_api_key=api_key)

# Vector search over the index
vector_store = PineconeVectorStore(index=pc.Index(settings.PINECONE_INDEX), embedding=embeddings)

# Hosted model that re-scores search results and keeps the best RAG_TOP_N
reranker = PineconeRerank(model=settings.PINECONE_RERANK_MODEL, top_n=settings.RAG_TOP_N, pinecone_api_key=api_key)
