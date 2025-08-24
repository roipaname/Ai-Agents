import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from scripts.agent import answer, db, embeddings
from utils.loader import load_any
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from scripts.ingest_new import ingest

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
    # Save uploaded file temporarily so ingest() can process it
    temp_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Call the existing ingest() function
    ingest(temp_path)

    return {"status": "ok", "file": file.filename}

# Run: uvicorn scripts.api:app --reload --port 8000
