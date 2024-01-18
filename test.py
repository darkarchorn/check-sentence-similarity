from sentence_transformers import SentenceTransformer, util

# Load the model
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

# Function to preprocess text
def preprocess(text):
    return text.lower()

# Read your data file and preprocess
# Assuming your data is in 'questions.txt'
questions = []
answers = []
with open('questions.txt', 'r') as file:
    for line in file:
        question, answer = line.strip().split('::')
        questions.append(preprocess(question))
        answers.append(preprocess(answer))

# Function to calculate similarities
def calculate_similarities(data):
    embeddings = model.encode(data)
    print(f"sdajdkj ewkjf q: {data}")
    return util.pytorch_cos_sim(embeddings, embeddings)

# Calculate similarities for questions and answers
question_similarities = calculate_similarities(questions)
answer_similarities = calculate_similarities(answers)

# Find and print top 3 similar question pairs and their corresponding answer similarities
for i in range(len(questions)):
    question_similarities[i][i] = -1  # Set self-similarity to a low value
    top_indices = question_similarities[i].argsort(descending=True)[:3]

    print(f"Top 3 similar questions for '{questions[i]}' with the answer '{answers[i]}':")
    for idx in top_indices:
        q_similarity = question_similarities[i][idx].item()
        a_similarity = answer_similarities[i][idx].item()
        print(f" - Q: '{questions[idx]}' | Similarity: {q_similarity:.4f}")
        print(f"   A: '{answers[idx]}' | Answer Similarity: {a_similarity:.4f}")
