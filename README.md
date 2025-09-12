# scripture_rag
A repo for me to play around with RAG (retrieval augmented generation) using LDS scriptures

## Usage: 

To set up your environment and download data, run `startup.sh`. This will download data into the `data`  directory and create an environment `ollama_env`

In order to run the python files, run `source ollama_env/bin/activate`. You will also need to have an ollama server running locally, and you need to have pulled the models for 'llama3' and 'nomic-embed-text'

To create the feature store which will be used in RAG, run `create_embeddings.py`. This will need to be done before running `answer_scripture_questions.py`

Finally, once the above steps are done, to ask a question about the scriptures run `answer_scripture_questions.py`.

## LangGraph Agent (New)

This codebase now includes a LangGraph-based agent that structures the flow as:

- Suggest: generate related questions to explore before retrieval.
- Retrieve: propose relevant scripture references and fetch their text.
- Verify: judge whether each retrieved reference is relevant and filter out the rest.

Files:
- `agents/state.py`: typed state for the graph.
- `agents/tools.py`: tools for follow-up question generation and relevance verification.
- `agents/graph.py`: builds the LangGraph and a helper `run_preanswer` entry point.

App integration:
- `app.py` now uses the agent for suggestions, retrieval, and verification (if `langgraph` is installed). It still streams the final answer with OpenAI as before.

Install:
- Add `langgraph` to your environment: `pip install -r requirements.txt`

Notes:
- If `langgraph` is not installed at runtime, the app falls back to the original retrieval behavior.
