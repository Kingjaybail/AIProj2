from typing import List, Tuple

def chunk_text(
    source_label: str,
    text: str,
    max_chars: int = 1000,
    overlap: int = 200,
) -> List[Tuple[str, str]]:
    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)
        chunk = text[start:end]
        chunks.append((source_label, chunk))
        if end == length:
            break
        start = end - overlap

    return chunks

def chunk_sources(
    source_texts: list[tuple[str, str]],
    max_chars: int = 1000,
    overlap: int = 200,
) -> list[tuple[str, str]]:
    all_chunks: list[tuple[str, str]] = []
    for label, txt in source_texts:
        all_chunks.extend(chunk_text(label, txt, max_chars, overlap))
    return all_chunks
