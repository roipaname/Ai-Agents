import os,re
from typing import List
from pathlib import path
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx