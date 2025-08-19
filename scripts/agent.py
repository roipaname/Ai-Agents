import os
from typing import List, Tuple
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from utils.web_tools import ddg_search, fetch_readable
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

load_dotenv()
BASE_MODEL = os.getenv("BASE_MODEL", "gpt2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DB_DIR = "storage/faiss"
LORA_DIR = "models/lora-lecture-gpt2"

# Load generator (base + LoRA if present)
tokenizer = AutoTokenizer.from_pretrained(LORA_DIR if os.path.exists(LORA_DIR) else BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    LORA_DIR if os.path.exists(LORA_DIR) else BASE_MODEL,
    device_map="auto"
)
model.eval()

# Load embeddings + FAISS
embedder = SentenceTransformer(EMBED_MODEL)
db = FAISS.load_local(DB_DIR, allow_dangerous_deserialization=True)

def retrieve(query: str, k: int = 4) -> List[Tuple[str, dict]]:
    qvec = embedder.encode([query], normalize_embeddings=True)
    docs = db.similarity_search_by_vector(qvec[0], k=k)
    return [(d.page_content, d.metadata) for d in docs]

PROMPT = """You are an expert assistant fine-tuned on my lectures.
Use the provided CONTEXT (from my lectures) and, if present, WEB_SNIPPETS (fresh info from the internet).
Cite inline with [L] for lecture chunks and [W] for web snippets.
Be precise and concise. If unsure, say so.

Question:
{question}

CONTEXT (Lectures):
{context}

WEB_SNIPPETS (Optional):
{web}

Answer:
"""

@torch.inference_mode()
def generate_answer(prompt: str, max_new_tokens: int = 280) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    out = model.generate(
        **inputs,
        do_sample=True,
        top_p=0.9,
        temperature=0.6,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.eos_token_id
    )
    txt = tokenizer.decode(out[0], skip_special_tokens=True)
    return txt.split("Answer:", 1)[-1].strip()

def answer(query: str, use_web: bool = True, k: int = 4):
    # 1) RAG from lectures
    chunks = retrieve(query, k=k)
    context = "\n\n".join(f"[L{i+1}] {c[:1200]}" for i,(c,_) in enumerate(chunks))

    # 2) Web (lightweight) if requested
    web_txt = ""
    if use_web:
        hits = ddg_search(query, max_results=3)
        snippets = []
        for i, h in enumerate(hits):
            try:
                text = fetch_readable(h["url"])[:1500]
                snippets.append(f"[W{i+1}] {h['title']}\n{text}\n(Source: {h['url']})")
            except Exception:
                continue
        web_txt = "\n\n".join(snippets)

    prompt = PROMPT.format(question=query, context=context, web=web_txt or "(none)")
    return generate_answer(prompt)

if __name__ == "__main__":
    print(answer("Summarize key ideas from lecture series on CNNs and any 2025 updates.", use_web=True))
