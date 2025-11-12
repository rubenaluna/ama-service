import logging
import os
from urllib.parse import urlparse

import chromadb
from dotenv import load_dotenv
from openai import OpenAI
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
CONTEXT_FILE_URL = os.getenv("CONTEXT_FILE_URL")

region = "us-east-2"


def download_object_text(bucket: str, key: str, encoding: str = "utf-8") -> str:
    client = boto3.session.Session(region_name=region).client("s3")

    try:
        response = client.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read()
        return body.decode(encoding)
    except (ClientError, BotoCoreError) as error:
        logger.error("Failed to download s3://%s/%s", bucket, key, exc_info=error)
        raise RuntimeError("Unable to download the requested S3 object.") from error


def load_context():
    chroma = chromadb.PersistentClient()
    collection = chroma.create_collection("context")

    client = OpenAI(api_key=API_KEY)

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
            yield " ".join(words[i : i + size])

    text = _load_context_text(CONTEXT_FILE_URL)

    chunks = list(chunk_text(text))

    for i, chunk in enumerate(chunks):
        emb = (
            client.embeddings.create(model="text-embedding-3-small", input=chunk)
            .data[0]
            .embedding
        )
        collection.add(ids=[f"chunk_{i}"], embeddings=[emb], documents=[chunk])

    print("Persisting Chroma collection to disk...")

    print(f"Stored {len(chunks)} chunks.")


if __name__ == "__main__":
    load_context()
