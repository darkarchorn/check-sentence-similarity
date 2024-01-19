from pydantic import BaseModel
from typing import List


class CreateData(BaseModel):
    level: str
    question: str
    explanation: str
    correct_answer: str
    incorrect_answers: List[str]

    class Config:
        arbitrary_types_allowed = True


class CreateQuestion(BaseModel):
    data: CreateData
    documentID: str
    prompt: str
    rating: int = 0
    active: bool = True
