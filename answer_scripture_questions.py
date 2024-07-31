import os
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

def interpret_verses(question, verses):
    messages = []
    
    verses_string = "\n".join(verses)
    sys_prompt = f"""
    You are a concise, faithful, and thoughtful latter-day saint. Your job is to answer your friend's question by quoting from some of the following scriptures: 
    {verses_string}

    Use some of the scriptures to support your thinking, but you don't have to quote from all of them. You should use three to five sentences to synthesize what is shared in the verses. and help your friend understand the answer to their question.
    
    """
    
    print("Here are some scriptures that may be helpful:")
    print(verses_string)

    client = OpenAI()
    response = client.chat.completions.create(
  model=GENERATIVE_MODEL,
  messages=[
    {"role": "system", "content": sys_prompt},
    {"role": "user", "content": question}
    ]
    )
    print(response.choices[0].message.content)

def answer_question(client, collection, num_verses = 5):
    question = input("Enter a question:\n")
    query_embedding = client.embeddings(model=EMBEDDINGS_MODEL, prompt=question)["embedding"]
    results = collection.query(query_embeddings=[query_embedding], n_results=num_verses)
    verses_list = []
    for i in range(len(results['documents'][0])):

        verses_list.append(results['ids'][0][i] + "; "  +results['documents'][0][i])
    response = interpret_verses(question, verses_list)


    return response

def main():
    client, collection = get_clients()
    answer_question(client, collection)
    
if __name__ == "__main__":
    main()
