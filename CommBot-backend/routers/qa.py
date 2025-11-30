from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import QAResponse

from services.extractor import extract_from_files, extract_from_urls
from services.llm_client import call_llm
from services.tokens import count_tokens

router = APIRouter(prefix="", tags=["qa"])


def trim_history_messages(messages, max_tokens=2000):
    trimmed = []
    total = 0

    for msg in reversed(messages):
        txt = f"{msg['role'].upper()}: {msg['text']}\n"
        token_count = count_tokens(txt)

        if total + token_count > max_tokens:
            break

        trimmed.append(msg)
        total += token_count

    return list(reversed(trimmed))


def simple_retrieve(all_sources: List[tuple], query: str, k: int = 5):
    query = query.lower()
    results = []

    for src, text in all_sources:
        score = sum(1 for w in query.split() if w in text.lower())
        results.append((score, src, text))

    results.sort(reverse=True, key=lambda x: x[0])

    top = [(src, text) for score, src, text in results[:k]]
    return top

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import QAResponse

import json

from db import get_chat
from services.extractor import extract_from_files, extract_from_urls
from services.llm_client import call_llm
from services.tokens import count_tokens  # fixed name
from services.chunker import chunk_sources
from services.retrieval import retrieve_top_k

router = APIRouter(prefix="", tags=["qa"])


def trim_history_messages(messages, max_tokens=2000):
    trimmed = []
    total = 0

    for msg in reversed(messages):  # newest first
        txt = f"{msg['role'].upper()}: {msg['text']}\n"
        token_count = count_tokens(txt)

        if total + token_count > max_tokens:
            break

        trimmed.append(msg)
        total += token_count

    return list(reversed(trimmed))  # restore original order


def simple_retrieve(all_sources: List[tuple], query: str, k: int = 5):
    query = query.lower()
    results = []

    for src, text in all_sources:
        score = sum(1 for w in query.split() if w in text.lower())
        results.append((score, src, text))

    results.sort(reverse=True, key=lambda x: x[0])
    top = [(src, text) for score, src, text in results[:k]]
    return top


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    chat_id: int = Form(...),
    prompt: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    urls: Optional[List[str]] = Form(None),
):
    print("\n====== NEW REQUEST ======")
    print(f"CHAT ID: {chat_id}")
    print(f"PROMPT: {prompt}")

    chat = get_chat(chat_id)
    all_history = json.loads(chat["messages"]) if chat else []

    trimmed_history = trim_history_messages(all_history, max_tokens=2000)

    history_text = "\n".join(
        f"{m['role'].upper()}: {m['text']}" for m in trimmed_history
    )

    files = files or []
    urls = urls or []

    file_sources = await extract_from_files(files)
    url_sources = extract_from_urls(urls)
    all_sources = file_sources + url_sources

    if all_sources:
        chunks = chunk_sources(all_sources)
        top_chunks = retrieve_top_k(chunks, prompt, k=5)
        context_text = "\n\n".join(
            f"SOURCE {src}:\n{text}" for src, text in top_chunks
        )
    else:
        context_text = ""
    llm_prompt = f"""
        You are a helpful assistant.
        
        Conversation so far:
        {history_text}
        
        Relevant extracted sources:
        {context_text}
        
        User message:
        {prompt}
        
        Respond using ONLY the conversation + sources above.
    """

    answer = call_llm(llm_prompt)

    used_sources = [src for src, _ in (top_chunks if all_sources else [])]

    return QAResponse(answer=answer, sources=used_sources)


