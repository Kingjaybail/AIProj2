import os
from typing import List, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = "gpt-4o"  # or "gpt-4o-mini" or "gpt-4.1"

def build_context_prompt(question: str, context_chunks: List[Tuple[str, str]]) -> str:
    print("getting response...")
    if not context_chunks:
        return question
    print(context_chunks)
    sources_text = "\n\n".join(
        f"### SOURCE: {src}\n{text}"
        for src, text in context_chunks
    )

    return f"""
            You are an AI assistant. 
            
            {sources_text}
            
            ### USER QUESTION
            {question}
            
            Give an answer based entirely on the sources above.
            If something is not included in the sources, say so.
            """


def call_llm(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()
