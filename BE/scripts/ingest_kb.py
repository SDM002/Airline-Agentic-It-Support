"""Loads the knowledge base documents into Pinecone. Run from BE/: python -m scripts.ingest_kb

Load -> chunk by headings -> (Pinecone embeds) -> store. Re-run whenever a document in data/kb changes.
"""

from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from app.config.settings import settings
from app.db.vector_store import pc, vector_store

# One chunk per SOP / policy section; the heading stays in the text so it is embedded too
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "document"), ("##", "section"), ("###", "sop")],
    strip_headers=False,
)

# Safety net for sections longer than RAG_CHUNK_SIZE
size_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.RAG_CHUNK_SIZE,
    chunk_overlap=settings.RAG_CHUNK_OVERLAP,
)

chunks = []
for path in sorted(Path(settings.RAG_KB_DIR).glob("*.md")):
    sections = header_splitter.split_text(path.read_text())
    for section in sections:
        section.metadata["source"] = path.name
    chunks += size_splitter.split_documents(sections)

# Start from an empty index so chunks from an older version of the documents are removed
if pc.Index(settings.PINECONE_INDEX).describe_index_stats().total_vector_count:
    vector_store.delete(delete_all=True)

ids = [f"{c.metadata['source']}-{i}" for i, c in enumerate(chunks)]
vector_store.add_documents(chunks, ids=ids)

print(f"Stored {len(chunks)} chunks in Pinecone index '{settings.PINECONE_INDEX}'.")
