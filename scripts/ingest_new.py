import os, sys
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from utils.loader import load_any

load_dotenv()
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

DB_DIR = "storage/faiss"

def ingest(path: str):
    txt = load_any(path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_text(txt)
    embedder = SentenceTransformer(EMBED_MODEL)
    vectors = embedder.encode(chunks, show_progress_bar=True, normalize_embeddings=True)
    db = FAISS.load_local(DB_DIR, allow_dangerous_deserialization=True)
    db.add_embeddings(embeddings=vectors, metadatas=[{"path": path}] * len(chunks), documents=chunks)
    db.save_local(DB_DIR)
    print(f"Added {len(chunks)} chunks from {path}")

if __name__ == "__main__":
    ingest(sys.argv[1])
