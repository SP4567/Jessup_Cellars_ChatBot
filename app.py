from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index2.html')

# Load the corpus
with open('Corpus.txt', 'r', encoding='utf-8') as f:
    corpus = f.read().split('\n\n')  # Assuming paragraphs are separated by blank lines

print("Corpus loaded. Number of paragraphs:", len(corpus))

# Load models
qa_model_name = "distilbert-base-cased-distilled-squad"
qa_tokenizer = AutoTokenizer.from_pretrained(qa_model_name)
qa_model = AutoModelForQuestionAnswering.from_pretrained(qa_model_name)
qa_pipeline = pipeline("question-answering", model=qa_model, tokenizer=qa_tokenizer)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
corpus_embeddings = embedding_model.encode(corpus)

print("Models loaded and corpus embeddings generated.")

def get_relevant_context(query, top_k=3):
    query_embedding = embedding_model.encode([query])
    similarities = cosine_similarity(query_embedding, corpus_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return ' '.join([corpus[i] for i in top_indices])

@app.route('/query', methods=['POST'])
def chat():
    data = request.json
    query = data['message']
    history = data.get('history', [])

    print("Received query:", query)

    context = get_relevant_context(query)

    # Check if query is about something in the corpus
    similarity_score = cosine_similarity(embedding_model.encode([query]), corpus_embeddings).max()
    print("Similarity score:", similarity_score)

    if similarity_score < 0.3:
        return jsonify({
            "response": "I'm sorry, I don't have information about that. Please contact the business directly for more details."
        })

    # Use QA model to generate response
    qa_input = {
        'question': query,
        'context': context
    }
    response = qa_pipeline(qa_input)
    print("QA response:", response)

    return jsonify({"response": response['answer']})

if __name__ == '__main__':
    app.run(debug=True)
