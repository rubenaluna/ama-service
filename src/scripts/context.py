import os, chromadb, logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(name)s:%(levelname)s: %(message)s"
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CONTEXT_FILE_PATH = os.getenv("CONTEXT_FILE_PATH")

client = OpenAI(api_key=OPENAI_API_KEY)
chroma = chromadb.PersistentClient()
collection = chroma.create_collection("context")


def chunk_text(text, size=500):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i : i + size])


with open(CONTEXT_FILE_PATH) as f:
    text = f.read()

chunks = list(chunk_text(text))

for i, chunk in enumerate(chunks):
    emb = (
        client.embeddings.create(model="text-embedding-3-small", input=chunk)
        .data[0]
        .embedding
    )
    collection.add(ids=[f"chunk_{i}"], embeddings=[emb], documents=[chunk])

logger.info(f"Stored {len(chunks)} chunks.")
