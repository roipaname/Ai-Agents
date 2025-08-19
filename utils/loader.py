import os,re
from typing import List
from pathlib import path
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx

def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
