import os
import sys
import ollama
import chromadb
from create_vector_store import EMBEDDINGS_MODEL, CHROMA_PATH, COLLECTION_NAME
from openai import OpenAI
from config import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

GENERATIVE_MODEL = "gpt-4o-mini"


def get_clients():
    client = ollama.Client()
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return (client, collection)

def combine_verses(documents, ids):
    """Combine verses together, so that any one verse only includes once and the verses are sorted. 
    
    """
    zfill_len = 5 ## We need to zfill to make sure that verse 10 comes after verse 9
    all_verses = dict()
    
    for i, cur_id in enumerate(ids):
        
        if cur_id.split(":")[1].find("-") < 0:
            all_verses[cur_id.split(":")[0] +":"+ cur_id.split(":")[1].zfill(zfill_len )] = documents[i]
        else:
            start_verse = int(cur_id.split(":")[1].split("-")[0])
            end_verse = int(cur_id.split(":")[1].split("-")[1])
            verses = documents[i].split("\n\n")
            cur_verse = start_verse
            while cur_verse <= end_verse:
                all_verses[cur_id.split(":")[0] +":"+ str(cur_verse).zfill(zfill_len )] = verses[cur_verse - start_verse]
                cur_verse += 1
    out_str = ""
    for idx in sorted(all_verses.keys()):
        out_str += idx.split(":")[0] + ":" + str(int(idx.split(":")[1])) + "\t"+ all_verses[idx] + "\n\n"
    return out_str
        

def interpret_verses(question, verses):
    messages = []
    
    sys_prompt = f"""
    You are a concise, faithful, and thoughtful latter-day saint. Your job is to answer your friend's question by quoting from some of the following scriptures: 
    {verses}

    Use some of the scriptures to support your thinking, but you don't have to quote from all of them. You should use three to five sentences to synthesize what is shared in the verses. and help your friend understand the answer to their question.
    
    """

    
    print("\nHere are some scriptures that may be helpful:\n")
    print(verses)

    client = OpenAI()
    response = client.chat.completions.create(
  model=GENERATIVE_MODEL,
  messages=[
    {"role": "system", "content": sys_prompt},
    {"role": "user", "content": question}
    ]
    )
    print(response.choices[0].message.content)

def answer_question(client, collection, num_verses = 10):
    question = input("Enter a question: (press enter to exit)\n")
    if question == "":
        return True
    query_embedding = client.embeddings(model=EMBEDDINGS_MODEL, prompt=question)["embedding"]
    results = collection.query(query_embeddings=[query_embedding], n_results=num_verses)
    verses = combine_verses(results['documents'][0], results['ids'][0])
    interpret_verses(question, verses)
    print("\n")
    return False


def main():
    client, collection = get_clients()
    completed = False
    while not completed:
        completed = answer_question(client, collection)
    
if __name__ == "__main__":
    main()
