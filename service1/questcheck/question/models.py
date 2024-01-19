from django.db import models
from sentence_transformers import SentenceTransformer, util
import uuid

def preprocess(text):
    return text.lower()

# Load the model
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

class Question(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=uuid.uuid4)
    data = models.JSONField()
    prompt = models.TextField()
    documentID = models.CharField(max_length=64, db_index=True)
    hashPrompt = models.CharField(max_length=64, db_index=True)
    rating = models.SmallIntegerField(default=0)
    active = models.BooleanField(default=True)
    embedding = models.JSONField()
    createdAt = models.DateTimeField(auto_now_add=True)

    def get_by_hash_prompt(self, hash_prompt):
        return Question.objects.filter(hashPrompt=hash_prompt)
    
    def get_question(self):
        questions = []
        answers = []
        try:
            items = self.data.get('parameters', {}).get('properties', {}).get('questions', {}).get('items', [])
            for item in items:
                questions.append(item.get('question'))
                answers.append(item.get('correct_answer'))
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
    def update_all_embeddings(cls, hashPrompt):
        for instance in cls.objects.filter(hashPrompt=hashPrompt):
            questions = instance.get_question()
            if questions:
                # Lowercase the questions and encode
                embeddings = model.encode([q.lower() for q in questions])
                # Convert numpy array to list
                instance.embedding = embeddings.tolist()
                instance.save()

    def check_existence(self, hash_prompt):
        existing_embedding = [q.embedding for q in questions]
        new_embedding = embed(self.data)
        max_similarity, _ = calculate_similarity(new_embedding, existing_embedding)
        max_similarity < 0.8

        questions = self.get_all_questions(hashPrompt=hash_prompt)
        
    
def calculate_similarity(data):
    embeddings = model.encode(data)
    return util.pytorch_cos_sim(embeddings, embeddings)

def embed(data):
    return model.encode(data)