import ollama
import chromadb
from create_vector_store import EMBEDDINGS_MODEL, CHROMA_PATH, COLLECTION_NAME

GENERATIVE_MODEL = "llama3"
def get_clients():
    client = ollama.Client()
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return (client, collection)

def interpret_verses(question, verses):
    verses_string = "Some scriptures that might help you with the answer to your question are:\n\n" + "\n".join(verses)
    prompt = f"""
    You are a concise, yet thoughtful latter-day saint seminary teacher. 
    
    Your job is to answer the following question:
    ```
    {question}
    ```

    Complete the following statement to share your response to the question. Use some of the scriptures to support your thinking, but you don't have to quote from all of them. You should use three to five sentences to synthesize what is shared in the verses.
    
    <<The response starts here>>
    {verses_string}
    
    """
    print(verses_string)
    results = ollama.generate(model=GENERATIVE_MODEL, prompt = prompt)
    print(results["response"])
    return (verses_string, results)

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
