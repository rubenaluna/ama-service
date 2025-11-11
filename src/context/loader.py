import os
from urllib.parse import urlparse

import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from s3 import download_object_text

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
CONTEXT_FILE_URL = os.getenv("CONTEXT_FILE_URL")

client = OpenAI(api_key=API_KEY)
chroma = chromadb.Client()
collection = chroma.create_collection("context")

def _load_context_text(path: str) -> str:
    if not path:
        raise ValueError("CONTEXT_FILE_URL is not set.")

    parsed = urlparse(path)

    bucket = parsed.netloc
    key = parsed.path.lstrip("/")
    return download_object_text(bucket, key)

def chunk_text(text, size=500):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])

text = _load_context_text(CONTEXT_FILE_URL)

chunks = list(chunk_text(text))

print(chunks)

for i, chunk in enumerate(chunks):
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunk
    ).data[0].embedding
    collection.add(
        ids=[f"chunk_{i}"],
        embeddings=[emb],
        documents=[chunk]
    )

print(f"Stored {len(chunks)} chunks.")