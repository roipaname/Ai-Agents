import os, sys
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.loader import load_any

load_dotenv()
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

DB_DIR = "storage/faiss"

def ingest(path: str):
    # Step 1: Load file text
    txt = load_any(path)

    # Step 2: Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_text(txt)

    # Step 3: Initialize embeddings (LangChain wrapper, not raw SentenceTransformer)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    # Step 4: Load existing FAISS DB
    db = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)

    # Step 5: Add new chunks
    db.add_texts(
        texts=chunks,
        metadatas=[{"path": path}] * len(chunks)
    )

    # Step 6: Save DB
    db.save_local(DB_DIR)
    print(f"Added {len(chunks)} chunks from {path}")

if __name__ == "__main__":
    ingest(sys.argv[1])
