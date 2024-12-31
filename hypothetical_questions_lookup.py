from create_vector_store import get_chroma_collection
from config import HYP_QUEST_COLLECTION_NAME, HYP_QUEST_EMBEDS_MODEL, HYP_QUEST_PATH, CHROMA_PATH, OPENAI_API_KEY, HYP_QUEST_ID_DELIM 
from openai import OpenAI
import os
import logging
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

NUM_VERSES_RANGE_EXTENSION = 3

def get_verse_range(input_verse):
    min_verse = int(input_verse.split("-")[0])
    try:
        max_verse = int(input_verse.split("-")[1])
    except ValueError:
        max_verse = min_verse
    return (min_verse, max_verse)

def get_ranged_references(input_reference):
    """Return a range of references around the current reference"""
    chapter = input_reference.split(":")[0]
    try:
        verse = int(input_reference.split(":")[1])
    except IndexError:
        return None
    min_verse, max_verse = get_verse_range(verse)
    return chapter + ":" + str(max(min_verse-NUM_VERSES_RANGE_EXTENSION, 1)) + "-" + str(max_verse + NUM_VERSES_RANGE_EXTENSION)



def get_verses(user_question, collection, embeddings_model = HYP_QUEST_EMBEDS_MODEL, num_verses = 7):
    client = OpenAI()
    query_embedding = client.embeddings.create(
        input=user_question,
        model=embeddings_model
    ).data[0].embedding
    results = collection.query(query_embeddings=[query_embedding], n_results=num_verses)
    return [get_ranged_references(x.split(HYP_QUEST_ID_DELIM)[0]) for x in results['ids'])]



