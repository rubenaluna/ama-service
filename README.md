# AMA Service

AMA (Ask Me Anything) Service is a lightweight GraphQL application that streams answers to questions about you. It combines OpenAI-powered generation with a Chroma vector store so responses can be grounded in a curated knowledge base.

## Project Highlights

- Real-time GraphQL subscription API built with Ariadne and Starlette.
- Retrieval-Augmented Generation (RAG) using a persistent Chroma database.
- OpenAI `gpt-4o-mini` for streaming chat completions and `text-embedding-3-small` for embeddings.
- Optional loader utility that ingests context from a local file and persists embeddings for inference.
- Simple Docker image and Uvicorn entrypoint for local or containerized deployments.

## Repository Layout

- `src/main.py` – ASGI entrypoint that wires the GraphQL schema.
- `src/api/api.py` – GraphQL subscription implementation that streams model output.
- `src/inference/inference.py` – Embedding, retrieval, and chat completion logic.
- `src/scripts/context.py` – Local helper that ingests a plain-text file and stores embeddings in Chroma.
- `chroma/` – On-disk vector store created by Chroma (generated after running the loader).
- `Dockerfile` – Container definition targeting Python 3.11 slim.

## Prerequisites

- Python 3.11+
- `pip` (or `uv`, `pipx`, etc.)
- OpenAI API access with billing enabled

## Environment Variables

| Variable            | Required | Description                                                            |
| ------------------- | -------- | ---------------------------------------------------------------------- |
| `OPENAI_API_KEY`    | Yes      | API key used for both embedding and chat completion requests.          |
| `CONTEXT_FILE_PATH` | Loader   | Absolute path to a local plain-text file for seeding the vector store. |
| `PORT`              | Optional | Port exposed by the ASGI app (defaults to `8000`).                     |

If you are supplying custom AWS credentials for the loader, rely on the standard AWS environment variables or configuration files (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.).

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Populate a `.env` file (or export variables) with the values in the table above.

## Building the Knowledge Base

Before you run the API, create or refresh the Chroma collection. Choose the option that matches your data source.

**Local file source (`src/scripts/context.py`):**

```bash
source .venv/bin/activate
python -m src.scripts.context
```

Set `CONTEXT_FILE_PATH` to the location of the file that should be embedded.

**Remote S3 source (`src/scripts/loader.py`):**

```bash
source .venv/bin/activate
python -m src.scripts.loader
```

Set `CONTEXT_FILE_PATH` to the local object path. This loader downloads file, chunks it, generates embeddings via OpenAI, and persists the collection to the `chroma/` directory.

Re-run either loader whenever the source content changes.

## Running the API (Local)

```bash
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

By default the service enables debug logging and loads environment variables via `python-dotenv` (`.env` in the project root).

## GraphQL Usage

The service exposes a single subscription `ask(question: String!): String!`. You can connect with a GraphQL IDE that supports subscriptions (e.g., Altair, GraphiQL with websockets, or Apollo Sandbox).

Example operation:

```graphql
subscription AskMe {
  ask(question: "What projects have you been working on lately?")
}
```

Each chunk streamed by the OpenAI API is forwarded to the client; the final empty string completes the subscription.

## Docker

Build and run the container:

```bash
docker build -t ama-service .
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e CONTEXT_FILE_PATH=$CONTEXT_FILE_PATH \
  -e CONTEXT_FILE_URL=$CONTEXT_FILE_URL \
  -v "$(pwd)/chroma:/app/chroma" \
  ama-service
```

Mount the `chroma/` directory so embeddings persist across container runs. Populate the collection on the host (recommended) or within the container by invoking the appropriate loader.

## Troubleshooting

- **Missing context**: Ensure the relevant loader (`src/scripts/context.py` or `src/scripts/loader.py`) has been run and the `chroma/` folder contains a `context` collection.
- **OpenAI errors**: Verify billing status and model availability; throttling or permission issues surface in the logs.

## Contributing

Issues and pull requests are welcome. When proposing changes, include steps to reproduce, updated documentation if needed, and note any additional environment requirements.
