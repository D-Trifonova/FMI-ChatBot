import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
from sentence_transformers import SentenceTransformer, util
import json


app = FastAPI()

# Load the scraped dataset
with open("fmi_full_site.json", "r", encoding="utf-8") as f:
    knowledge_base = json.load(f)

# Extract document data
documents = [entry["content"] for entry in knowledge_base]
document_titles = [entry["title"] for entry in knowledge_base]
document_urls = [entry["url"] for entry in knowledge_base]

# Load sentence transformer for semantic search
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
document_embeddings = embedding_model.encode(documents, convert_to_tensor=True)

# Load the GPT-2 model and tokenizer
model_path = "../FMI-ChatBot-backup/runs/Jan12_16-39-00_7dbf5bb81ad5"
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)

# Initialize GPT-2 pipeline
gpt2_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)


# Define the request model
class ChatRequest(BaseModel):
    question: str


def get_relevant_context_from_sql(question, db_path="DB./documents.db"):
    """
    Retrieve the most relevant context from the SQL database for the given question.

    Args:
        question (str): The user's question.
        db_path (str): Path to the SQLite database.

    Returns:
        dict: A dictionary containing the matched content, title, and URL.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Retrieve all documents for semantic search
        cursor.execute("SELECT id, title, content, url FROM documents")
        rows = cursor.fetchall()

        # Extract fields
        ids = [row[0] for row in rows]
        titles = [row[1] for row in rows]
        contents = [row[2] for row in rows]
        urls = [row[3] for row in rows]

        # Perform semantic search
        document_embeddings = embedding_model.encode(contents, convert_to_tensor=True)
        query_embedding = embedding_model.encode(question, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(query_embedding, document_embeddings)
        best_match_idx = scores.argmax().item()  # Index of the most relevant document

        # Get the best match details
        return {
            "title": titles[best_match_idx],
            "content": contents[best_match_idx],
            "url": urls[best_match_idx],
        }

    except Exception as e:
        raise ValueError(f"Error querying database: {e}")
    finally:
        conn.close()


@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Step 1: Retrieve the relevant context from the SQL database
        relevant_context = get_relevant_context_from_sql(request.question)
        title = relevant_context["title"]
        content = relevant_context["content"]
        url = relevant_context["url"]

        # Step 2: Use GPT-2 to generate an answer based on the context
        prompt = f"Question: {request.question}\nContext: {content}\nAnswer:"
        gpt2_result = gpt2_pipeline(prompt, max_length=200, num_return_sequences=1, temperature=0.7)

        # Extract the generated GPT-2 answer
        gpt2_answer = gpt2_result[0]["generated_text"].split("Answer:")[-1].strip()

        # Step 3: Shorten the context for the response
        context_excerpt = content[:200] + "..." if len(content) > 200 else content

        # Return the relevant data along with the GPT-2 answer
        return {
            "answer": gpt2_answer,
            "title": title,
            "context_excerpt": context_excerpt,
            "url": url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
