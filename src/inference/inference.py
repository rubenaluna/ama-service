import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import chromadb
import logging

logger = logging.getLogger(__name__)

load_dotenv()

TOP_K = 3
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NAME = os.getenv("NAME")
EMAIL = os.getenv("EMAIL")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
chroma = chromadb.PersistentClient()


async def embed(text: str) -> list[float]:
    emb = await client.embeddings.create(model="text-embedding-3-small", input=text)
    return emb.data[0].embedding


def build_messages(context: str, question: str):
    return [
        {
            "role": "system",
            "content": 'You are a chatbot representing the person described in the context. \
                Be factual and concise. Use first person ("I") to speak as that person. \
                Reference content only from this context when possible. \
                If you can\'t answer a question about the person, suggest contacting them directly.',
        },
        {"role": "system", "content": f"Context:\\n{context}"},
        {"role": "user", "content": question},
    ]


async def infer(question: str) -> str:
    qvec = await embed(question)

    collection = chroma.get_collection("context")
    results = collection.query(query_embeddings=[qvec], n_results=TOP_K)
    docs = results.get("documents", [[]])[0] if results else []

    context = "\n\n".join(docs) if docs else "No retrieved context."

    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=build_messages(context, question),
        stream=True,
    )

    return stream
