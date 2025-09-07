# scripture_rag
A repo for me to play around with RAG (retrieval augmented generation) using LDS scriptures

## Usage: 

To set up your environment and download data, run `startup.sh`. This will download data into the `data`  directory and create an environment `ollama_env`

In order to run the python files, run `source ollama_env/bin/activate`. You will also need to have an ollama server running locally, and you need to have pulled the models for 'llama3' and 'nomic-embed-text'

To create the feature store which will be used in RAG, run `create_embeddings.py`. This will need to be done before running `answer_scripture_questions.py`

Finally, once the above steps are done, to ask a question about the scriptures run `answer_scripture_questions.py`.

## Using a standalone Chroma FastAPI server

You can run ChromaDB as its own FastAPI server and point the code at it:

- Start the Chroma server (ensure `chromadb` is installed in your venv):
  - `./run_chroma_server.sh`
  - or manually: `chroma run --path chroma_dir --host 0.0.0.0 --port 8000`

- Configure clients to use the server by editing `config.py`:
  - `CHROMA_USE_HTTP = True`
  - `CHROMA_SERVER_HOST = "localhost"` (or your host/IP)
  - `CHROMA_SERVER_HTTP_PORT = 8000`

With this configuration, `create_vector_store.py` and `answer_scripture_questions.py` connect to the Chroma server via REST and store/query vectors on that server.

## Retrieval FastAPI Service

This repo now includes a standalone FastAPI microservice that wraps the scripture retrieval logic from `llm_retrieval.py`.

- Start the service (ensure dependencies are installed):
  - `uvicorn retrieval_service:app --host 0.0.0.0 --port 8001`

- Endpoint:
  - `POST /retrieve`
    - Request body: `{ "question": "<your question>", "generative_model": "gpt-4o-mini" }`
    - Response: `{ "scriptures_string": "<tab-separated scripture refs and text>" }`

- Health check:
  - `GET /health` -> `{ "status": "ok" }`

The service initializes the scriptures index and a Chroma collection on startup. It supports using a standalone Chroma server when configured via `config.py` (`CHROMA_USE_HTTP`, `CHROMA_SERVER_HOST`, `CHROMA_SERVER_HTTP_PORT`).
