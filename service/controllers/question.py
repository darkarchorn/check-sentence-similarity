import hashlib
from fastapi import Depends
from sentence_transformers import SentenceTransformer, util
import os
from sqlalchemy.orm import Session
from database import getDatabase
from models.question import QuestionModel
from schemas.question import CreateQuestion

model = SentenceTransformer("distilbert-base-nli-mean-tokens")


class QuestionController:
    def set_data(db: Session = Depends(getDatabase)):
        with open(os.getcwd() + "/questions.txt", "r") as file:
            lines = file.readlines()

        for line in lines:
            data = line.strip().split("::")
            hashPrompt = hashlib.sha256(data[0].encode("utf-8")).hexdigest()
            embeddings = model.encode([q.lower() for q in data[1]])
            newQuestion = QuestionModel(
                data={
                    "level": "Trung bình",
                    "question": data[1],
                    "explanation": data[1] + " " + data[0],
                    "correct_answer": data[2],
                    "incorrect_answers": [data[2] + "1", data[2] + "2", data[2] + "3"],
                },
                documentID="13dQVuPeiyn0ue4Fc50eepiorBUN9zBy0FN7zNGZdjoI",
                prompt=data[0],
                hashPrompt=hashPrompt,
                embedding=embeddings.tolist(),
                rating=0,
                active=True,
            )
            db.add(newQuestion)
            db.commit()
        return {"msg": "successful!"}

    def create_quest(self, payload: CreateQuestion, db: Session = Depends(getDatabase)):
        hashPrompt = hashlib.sha256(payload.prompt.encode("utf-8")).hexdigest()
        embeddings = model.encode([q.lower() for q in payload.data.question])
        newQuestion = QuestionModel(
            data={
                "level": payload.data.level,
                "question": payload.data.question,
                "explanation": payload.data.explanation,
                "correct_answer": payload.data.correct_answer,
                "incorrect_answers": payload.data.incorrect_answers,
            },
            documentID=payload.documentID,
            prompt=payload.documentID,
            hashPrompt=hashPrompt,
            embedding=embeddings.tolist(),
            rating=payload.rating,
            active=payload.active,
        )
        res, quest = self.check_existence(payload.data.question, hashPrompt, db)
        return quest

    def get_by_hash_prompt(self, hash_prompt: str, db: Session = Depends(getDatabase)):
        object = (
            db.query(QuestionModel)
            .filter(QuestionModel.hashPrompt == hash_prompt)
            .all()
        )
        return object

    def check_existence(
        self, new_question, hash_prompt, db: Session = Depends(getDatabase)
    ):
        instances = self.get_by_hash_prompt(hash_prompt, db)
        all_embeddings = []
        all_questions = []
        # Collect all embeddings from the instances
        for instance in instances:
            if instance.embedding:
                all_embeddings.append(instance.embedding)
                all_questions.append(instance.data)

        # Encode all questions to get their embeddings
        quest_arr = []

        for question in all_questions:
            quest_arr.append(question["question"])
        quest_arr.append(new_question)
        embeddings = model.encode(quest_arr)

        # Compute cosine similarity
        similarity = util.pytorch_cos_sim(embeddings, embeddings)

        # Set self-similarity to -1
        similarity[-1][-1] = -1

        # Find the most similar question
        top_similarity, top_index = similarity[-1].topk(4, largest=True)
        for i in range(len(top_similarity)):
            print(all_questions[i])

        # Check if the most similar question is above the threshold
        if top_similarity[0].item() > 0.9:
            return True, [
                all_questions[top_index[i].item()]["question"] for i in range(4)
            ]
        return False, None
