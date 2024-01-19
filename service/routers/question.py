from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from controllers.question import QuestionController
from database import getDatabase
from schemas.question import CreateQuestion


router = APIRouter(prefix="/question", tags=["question"])


@router.get("/")
def set_data(db: Session = Depends(getDatabase)):
    return QuestionController.set_data(db=db)


@router.post("/create")
def create_if_not_exists(payload: CreateQuestion, db: Session = Depends(getDatabase)):
    questionController = QuestionController()
    return questionController.create_quest(payload=payload, db=db)
