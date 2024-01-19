from pydantic import BaseModel


class CreateData(BaseModel):
    level: str
    question: str
    explanation: str
    correct_answer: str
    incorrect_answers: list()

    class Config:
        arbitrary_types_allowed = True


class CreateQuestion(BaseModel):
    data: CreateData
    documentID: str
    prompt: str
    rating: int = 0
    active: bool = True
