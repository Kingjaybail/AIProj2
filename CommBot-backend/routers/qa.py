import json

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import QAResponse
from db import get_chat
from services.extractor import extract_from_files, extract_from_urls
from services.llm_client import call_llm
from services.tokens import count_tokens
from services.chunker import chunk_sources
from services.retrieval import retrieve_top_k

router = APIRouter(prefix="", tags=["qa"])


# -----------------------------
#  Trim history tokens
# -----------------------------
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

    return list(reversed(trimmed))



# -----------------------------
#  Main ASK Route
# -----------------------------
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
    print(f"Files: {files}")
    print(f"URLS (raw): {urls}")

    # ---------------------------------
    # Load chat history
    # ---------------------------------
    chat = get_chat(chat_id)
    all_history = json.loads(chat["messages"]) if chat else []
    trimmed_history = trim_history_messages(all_history)
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['text']}" for m in trimmed_history
    )

    # ---------------------------------
    # Sanitize URLs
    # ---------------------------------
    if urls is None:
        urls = []
    elif isinstance(urls, str):
        urls = [urls]

    urls = [u.strip() for u in urls if u and u.strip()]
    urls = list(dict.fromkeys(urls))  # dedupe, preserve order

    print(f"URLS (clean): {urls}")

    # ---------------------------------
    # Sanitize FILES (dedupe by filename)
    # ---------------------------------
    files = files or []

    seen_filenames = set()
    unique_files = []
    for f in files:
        if f.filename not in seen_filenames:
            seen_filenames.add(f.filename)
            unique_files.append(f)

    files = unique_files
    print(f"FILES (clean): {[f.filename for f in files]}")

    # ---------------------------------
    # Extract text from sources
    # ---------------------------------
    file_sources = await extract_from_files(files)
    url_sources = extract_from_urls(urls)

    first_source = []

    if file_sources:
        first_source = [file_sources[0]]
    elif url_sources:
        first_source = [url_sources[0]]

    all_sources = first_source
    print(f"SOURCE COUNT: {len(all_sources)}")

    # ---------------------------------
    # Build context from top source chunks
    # ---------------------------------
    if all_sources:
        chunks = chunk_sources(all_sources)
        top_chunks = retrieve_top_k(chunks, prompt, k=5)

        context_text = "\n\n".join(
            f"SOURCE {src}:\n{text}" for src, text in top_chunks
        )
    else:
        top_chunks = []
        context_text = ""

    # ---------------------------------
    # Build final LLM Prompt
    # ---------------------------------
    llm_prompt = f"""
        You are a helpful assistant.
        
        Conversation so far:
        {history_text}
        
        Relevant extracted sources:
        {context_text}
        
        User message:
        {prompt}
        
        Respond using ONLY the conversation + sources above.
        
        In the situation that no sources are provided respond normally do not mention the lack of sources
    """

    # ---------------------------------
    # Call LLM
    # ---------------------------------
    answer = call_llm(llm_prompt)

    used_sources = list(dict.fromkeys(src for src, _ in top_chunks))

    return QAResponse(
        answer=answer,
        sources=used_sources
    )
