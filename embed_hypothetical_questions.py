from create_vector_store import get_chroma_collection
from config import HYP_QUEST_COLLECTION_NAME, HYP_QUEST_EMBEDS_MODEL, HYP_QUEST_PATH, CHROMA_PATH, OPENAI_API_KEY, HYP_QUEST_ID_DELIM 
from openai import OpenAI
import os
import logging
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def add_to_collection_openai(hypothetical_question, collection, id_num, embeddings_model = HYP_QUEST_EMBEDS_MODEL):
    if (id_num % 1000) == 0:
        logger.info(f"Running for id {id_num}")
    try:
        question_only = hypothetical_question.split(":")[1].split(" ")[1] ## each question starts with a chapter reference, and we want to chop that off so the embedings don't take it as input
        id_only = (hypothetical_question.split(":")[0] + ":" + hypothetical_question.split(":")[1].split(" ")[0] ).replace(HYP_QUEST_ID_DELIM, "") + HYP_QUEST_ID_DELIM  + str(id_num)
    except IndexError:
        return
    client = OpenAI()
    embedding = client.embeddings.create(
        input=question_only,
        model=embeddings_model
    ).data[0].embedding
    collection.add(ids = [id_only],
                   embeddings = [embedding],
                       documents = [hypothetical_question])

def main():
    collection = get_chroma_collection(CHROMA_PATH, collection_name = HYP_QUEST_COLLECTION_NAME)
    with open(HYP_QUEST_PATH, 'r') as hq_file:
        for i, line in enumerate(hq_file):
            add_to_collection_openai(line, collection, id_num = i, embeddings_model = HYP_QUEST_EMBEDS_MODEL)

if __name__ == "__main__":
    main()





