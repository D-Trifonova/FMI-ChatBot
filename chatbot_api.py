import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
from sentence_transformers import SentenceTransformer, util
import json
import faiss
import numpy as np

# Connect to the database and load embeddings
conn = sqlite3.connect("DB/documents.db")
cursor = conn.cursor()
cursor.execute("SELECT embedding FROM documents")
rows = cursor.fetchall()
embeddings = np.array([np.frombuffer(row[0], dtype=np.float32) for row in rows])

# Build the Faiss index
embedding_size = embeddings.shape[1]
index = faiss.IndexFlatL2(embedding_size)
index.add(embeddings)

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
        # Step 1: Encode the question
        query_embedding = embedding_model.encode(request.question, convert_to_tensor=True).cpu().numpy()
        query_embedding = query_embedding.reshape(1, -1)
        print(f"Query Embedding Shape After Reshape: {query_embedding.shape}")

        # Step 2: Perform Faiss search
        D, I = index.search(query_embedding, k=1)
        print(f"Faiss Search Results - Distances: {D}, Indices: {I}")

        # Validate Faiss result
        if I[0][0] == -1:
            raise HTTPException(status_code=404, detail="No relevant documents found in Faiss index.")

        best_match_idx = int(I[0][0])  # Ensure the index is an integer
        print(f"Best match index: {best_match_idx}")

        # Step 3: Query the SQL database
        cursor.execute("SELECT COUNT(*) FROM documents")
        row_count = cursor.fetchone()[0]
        print(f"Total rows in the table: {row_count}")

        # Ensure the index is within the range of rows
        if best_match_idx >= row_count:
            raise HTTPException(
                status_code=500,
                detail=f"Index {best_match_idx} out of range for table with {row_count} rows."
            )

        # Fetch the matching document
        cursor.execute("SELECT title, content, url FROM documents LIMIT 1 OFFSET ?", (best_match_idx,))
        result = cursor.fetchone()
        print(f"SQL Query Result: {result}")

        # Ensure the result contains all expected fields
        if not result or len(result) != 3:
            raise HTTPException(status_code=404, detail="No valid document found in the database.")

        title, content, url = result

        # Step 4: Generate a response using GPT-2
        gpt2_response = gpt2_pipeline(request.question, max_length=100, num_return_sequences=1)

        # Step 5: Return the response
        return {
            "answer": gpt2_response[0]['generated_text'] if gpt2_response else "No answer generated.",
            "title": title,
            "context_excerpt": content[:200] + "...",
            "url": url,
        }

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=f"ValueError during processing: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during processing: {e}")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
