from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    JSON,
    Text,
    SmallInteger,
    Boolean,
    DateTime,
)
from datetime import datetime
import database


class QuestionModel(database.Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)
    prompt = Column(Text)
    documentID = Column(String(64), index=True)
    hashPrompt = Column(String(64), index=True)
    rating = Column(SmallInteger, default=0)
    active = Column(Boolean, default=0)
    embedding = Column(JSON)
    createdAt = Column(DateTime, default=datetime.now())
