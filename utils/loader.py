import os,re
from typing import List
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx

def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
def load_pdf(path:str)->str:
    elements=partition_pdf(filname=path)
    return "\n".join(e.text for e in elements if getattr(e, "text", None))
def load_docx(path:str)->str:
    elements = partition_docx(filename=path)
    return "\n".join(e.text for e in elements if getattr(e, "text", None))
def load_only(path:str)->str:
    ext=Path(path).suffix.lower()
    if ext ==".txt":
        return load_txt(path)
    elif ext==".pdf":
        return load_pdf(path)
    elif ext==".docx":
        return load_docx(path)