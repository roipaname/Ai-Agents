import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from utils.loader import collect_files, load_any

load_dotenv()
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

DATA_DIR = "data/lectures"
DB_DIR = "storage/faiss"

def main():
    files = collect_files(DATA_DIR)
    docs, metadatas = [], []
    for fp in files:
        txt = load_any(fp)
        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
        chunks = splitter.split_text(txt)
        docs.extend(chunks)
        metadatas.extend([{"path": fp}] * len(chunks))

    embedder = SentenceTransformer(EMBED_MODEL)
    vectors = embedder.encode(docs, show_progress_bar=True, normalize_embeddings=True)

    os.makedirs(DB_DIR, exist_ok=True)
    db = FAISS.from_embeddings(embeddings=vectors, metadatas=metadatas, documents=docs)
    db.save_local(DB_DIR)
    print(f"Saved FAISS DB to {DB_DIR} with {len(docs)} chunks.")

if __name__ == "__main__":
    main()
