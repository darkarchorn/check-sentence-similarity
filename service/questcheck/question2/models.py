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
    embedding = models.JSONField()

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
        print(f"abc: {hashPrompt}")
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
        instances = cls.get_by_hash_prompt(hash_prompt)
        all_embeddings = []
        all_questions = []

        # Collect all embeddings from the instances
        for instance in instances:
            if instance.embedding:
                all_embeddings.append(instance.embedding)
                all_questions.append(instance.data)

        # Add the new question for batch processing
        all_questions.append(new_question)

        # Encode all questions to get their embeddings
        embeddings = model.encode(all_questions)

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
            return True, [all_questions[top_index[i].item()] for i in range(4)]
        return False, None
