import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from scripts.agent import answer, db, embedder
from utils.loaders import load_any
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
PORT = int(os.getenv("PORT", "8000"))

app = FastAPI(title="Lecture RAG Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.post("/ask")
async def ask(q: str = Form(...), use_web: bool = Form(True)):
    resp = answer(q, use_web=use_web)
    return {"answer": resp}

@app.post("/add")
async def add(file: UploadFile = File(...)):
    content = (await file.read()).decode(errors="ignore")
    # if it's not text, try loader route (e.g., pdf bytes) — for brevity assume text here
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_text(content)
    vectors = embedder.encode(chunks, normalize_embeddings=True)
    FAISS_store = db  # reuse loaded DB from scripts.agent import
    FAISS_store.add_embeddings(embeddings=vectors, metadatas=[{"path": file.filename}] * len(chunks), documents=chunks)
    FAISS_store.save_local("storage/faiss")
    return {"status":"ok", "chunks_added": len(chunks)}

# Run: uvicorn scripts.api:app --reload --port 8000
