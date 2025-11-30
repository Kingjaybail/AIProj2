import os
from typing import List
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"  # change if desired

def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 1536), dtype="float32")

    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    vectors = [item.embedding for item in resp.data]
    return np.array(vectors, dtype="float32")
