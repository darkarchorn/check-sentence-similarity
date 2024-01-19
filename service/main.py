from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import question

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(router=question.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "sentry-trace", "baggage"],
)
