# scripture_rag
A repo for me to play around with RAG (retrieval augmented generation) using LDS scriptures

## Usage: 

To set up your environment and download data, run `startup.sh`. This will download data into the `data`  directory and create an environment `ollama_env`

In order to run the python files, run `source ollama_env/bin/activate`. You will also need to have an ollama server running locally, and you need to have pulled the models for 'llama3' and 'nomic-embed-text'

To create the feature store which will be used in RAG, run `create_embeddings.py`. This will need to be done before running `answer_scripture_questions.py`

Finally, once the above steps are done, to ask a question about the scriptures run `answer_scripture_questions.py`.
