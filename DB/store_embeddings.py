import sqlite3
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda' if torch.cuda.is_available() else 'cpu')

# Connect to SQLite database
conn = sqlite3.connect("documents.db")
cursor = conn.cursor()

# Add embedding column if not exists
cursor.execute("ALTER TABLE documents ADD COLUMN embedding BLOB")

# Precompute embeddings
cursor.execute("SELECT id, content FROM documents")
rows = cursor.fetchall()

for doc_id, content in rows:
    embedding = model.encode(content).astype(np.float32).tobytes()
    cursor.execute("UPDATE documents SET embedding = ? WHERE id = ?", (embedding, doc_id))

conn.commit()
conn.close()

print("Embeddings precomputed and stored in the database.")
