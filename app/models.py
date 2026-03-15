from pydantic import BaseModel
from typing import List, Dict, Optional

class DeidRequest(BaseModel):
    text: str
    mode: str = "mask"

class BatchDeidRequest(BaseModel):
    texts: List[str]
    mode: str = "mask"

class Entity(BaseModel):
    start: int
    end: int
    label: str
    text: str
    source: str
    score: Optional[float] = None

class DeidResponse(BaseModel):
    original: str
    deidentified: str
    entities: List[Entity]

class BatchDeidResponse(BaseModel):
    results: List[DeidResponse]

class FeedbackRequest(BaseModel):
    original_text: str
    corrected_text: str
    entities: List[Entity]
    comment: Optional[str] = None
