"""Ingestion pipeline: chunk the documents in RAG_KB_DIR and store them in Pinecone. Run from BE/: python -m scripts.ingest_kb"""

from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.config.settings import settings
from app.db.vector_store import pc, vector_store

# Split by headings: one chunk per SOP / policy section, heading kept in the text
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "document"), ("##", "section"), ("###", "sop")],
    strip_headers=False,
)

# Split sections longer than RAG_CHUNK_SIZE, with overlap
size_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.RAG_CHUNK_SIZE,
    chunk_overlap=settings.RAG_CHUNK_OVERLAP,
)

# Load and chunk every document, tagging each chunk with its file name
chunks = []
for path in sorted(Path(settings.RAG_KB_DIR).glob("*.md")):
    sections = header_splitter.split_text(path.read_text())
    for section in sections:
        section.metadata["source"] = path.name
    chunks += size_splitter.split_documents(sections)

# Empty the index so chunks from older document versions are removed
if pc.Index(settings.PINECONE_INDEX).describe_index_stats().total_vector_count:
    vector_store.delete(delete_all=True)

# Embed (by Pinecone) and store, with stable IDs
ids = [f"{c.metadata['source']}-{i}" for i, c in enumerate(chunks)]
vector_store.add_documents(chunks, ids=ids)

print(f"Stored {len(chunks)} chunks in Pinecone index '{settings.PINECONE_INDEX}'.")
