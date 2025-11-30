from pydantic import BaseModel
from typing import List

class QAResponse(BaseModel):
    answer: str
    sources: List[str]
