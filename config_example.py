import os
OPENAI_API_KEY=''

DATA_PATH = os.path.join('data','scriptures.txt')
EMBEDDINGS_MODEL = 'nomic-embed-text'
CHROMA_PATH = "chroma_dir"
COLLECTION_NAME = "verses"

# Chroma server configuration
# Always use the standalone Chroma FastAPI server via HTTP.
CHROMA_USE_HTTP = True
CHROMA_SERVER_HOST = os.environ.get("CHROMA_SERVER_HOST", "localhost")
CHROMA_SERVER_HTTP_PORT = int(os.environ.get("CHROMA_SERVER_HTTP_PORT", "8000"))


HYP_QUEST_COLLECTION_NAME = "hypothetical_question"
HYP_QUEST_EMBEDS_MODEL = "text-embedding-3-small"
HYP_QUEST_PATH = os.path.join('data','hypothetical_questions.txt')
HYP_QUEST_ID_DELIM = "|"
