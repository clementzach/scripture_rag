import os
OPENAI_API_KEY=''

DATA_PATH = os.path.join('data','scriptures.txt')
EMBEDDINGS_MODEL = 'nomic-embed-text'
CHROMA_PATH = "chroma_dir"
COLLECTION_NAME = "verses"
HYP_QUEST_COLLECTION_NAME = "hypothetical_question"
HYP_QUEST_EMBEDS_MODEL = "text-embedding-3-small"
HYP_QUEST_PATH = os.path.join('data','hypothetical_questions.txt')
HYP_QUEST_ID_DELIM = "|"
