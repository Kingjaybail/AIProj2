from typing import List, Tuple
from fastapi import UploadFile
import requests
from bs4 import BeautifulSoup
from docx import Document
from io import BytesIO
from PyPDF2 import PdfReader

def _read_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")

def _read_docx(content: bytes) -> str:
    doc = Document(BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs)

def _read_pdf(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)

async def extract_from_files(files: List[UploadFile]) -> List[Tuple[str, str]]:
    print(files)
    results = []

    for f in files:
        ext = (f.filename or "").lower()

        # Reset pointer before reading
        try:
            f.file.seek(0)
        except Exception:
            pass

        data = await f.read()
        text = ""

        try:
            if ext.endswith(".txt"):
                text = _read_txt(data)
            elif ext.endswith(".docx") or ext.endswith(".doc"):
                text = _read_docx(data)
            elif ext.endswith(".pdf"):
                text = _read_pdf(data)
            else:
                continue
        except Exception as e:
            print("Error reading file:", f.filename, e)
            continue

        if text.strip():
            results.append((f"file:{f.filename}", text))

    return results




def extract_from_urls(urls: List[str]) -> List[Tuple[str, str]]:
    results = []
    for url in urls:
        url = url.strip()
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=" ")
            text = " ".join(text.split())
            if text:
                results.append((f"url:{url}", text))
        except Exception:
            continue
    return results
