from sentence_transformers import SentenceTransformer, util

def preprocess(text):
    return text.lower()

# Load the model
model = SentenceTransformer('distilbert-base-nli-mean-tokens')