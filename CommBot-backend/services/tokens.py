import tiktoken

# choose the encoding based on your model
ENCODING = tiktoken.encoding_for_model("gpt-4.1-mini")

def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))
