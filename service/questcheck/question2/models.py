import hashlib
from django.db import models
from sentence_transformers import SentenceTransformer, util
import uuid
import os


def preprocess(text):
    return text.lower()


# Load the model
model = SentenceTransformer("distilbert-base-nli-mean-tokens")


class Question2(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=uuid.uuid4)
    data = models.TextField()
    answer = models.TextField()
    prompt = models.TextField()
    hashPrompt = models.CharField(max_length=64, db_index=True)
    embedding = models.TextField()

    class Meta:
        db_table = "question2"

    def set_data(self):
        with open(os.getcwd() + "/questions.txt", "r") as file:
            lines = file.readlines()

        for line in lines:
            data = line.strip().split("::")
            hashPrompt = hashlib.sha256(data[0].encode("utf-8")).hexdigest()
            embeddings = model.encode([q.lower() for q in data[1]])
            question_instance = Question2(
                id=str(uuid.uuid4()),
                data=data[1],
                answer=data[2],
                prompt=data[0],
                hashPrompt=hashPrompt,
                embedding=embeddings.tolist(),
            )

            question_instance.save()

    def create_quest(self, request):
        hashPrompt = hashlib.sha256(request.data["prompt"].encode("utf-8")).hexdigest()
        embeddings = model.encode([q.lower() for q in request.data["question"]])
        question_instance = Question2(
            id=str(uuid.uuid4()),
            data=request.data["question"],
            answer=request.data["answer"],
            prompt=request.data["prompt"],
            hashPrompt=hashPrompt,
            embedding=embeddings.tolist(),
        )
        res, quest = self.check_existence(request.data["question"], hashPrompt)
        print(res)
        print(quest)

    @classmethod
    def get_by_hash_prompt(self, hash_prompt):
        return Question2.objects.filter(hashPrompt=hash_prompt)

    def get_question(self):
        questions = []
        answers = []
        try:
            items = (
                self.data.get("parameters", {})
                .get("properties", {})
                .get("questions", {})
                .get("items", [])
            )
            for item in items:
                questions.append(item.get("question"))
                answers.append(item.get("correct_answer"))
            return questions, answers
        except (AttributeError, TypeError, KeyError):
            return None, None

    @classmethod
    def get_all_questions(cls, hashPrompt):
        all_questions = []
        all_answers = []
        for instance in cls.objects.filter(hashPrompt=hashPrompt):
            questions, answers = instance.get_question()
            all_questions.extend(questions)
            all_answers.extend(answers)
        return all_questions, all_answers

    @classmethod
    def update_all_embeddings(cls, hash_prompt):
        for instance in cls.objects.filter(hashPrompt=hash_prompt):
            questions = instance.get_question()
            if questions:
                # Lowercase the questions and encode
                embeddings = model.encode([q.lower() for q in questions])
                # Convert numpy array to list
                instance.embedding = embeddings.tolist()
                instance.save()

    @classmethod
    def check_existence(cls, new_question, hash_prompt):
        new_question_embedding = model.encode(new_question)
        instances = cls.objects.filter(hashPrompt=hash_prompt)
        all_embeddings = []
        all_questions = []

        # Collect all embeddings from the instances
        for instance in instances:
            if instance.embedding:
                all_embeddings.extend(instance.embedding)
                question = instance.data
                all_questions.extend(question)

        # Check for cosine similarity between each pair of embeddings
        for i in range(len(all_embeddings)):
            similarity = util.pytorch_cos_sim(all_embeddings[i], new_question_embedding)
            if similarity > 0.9:
                return True, all_questions[i]
        return False, None
