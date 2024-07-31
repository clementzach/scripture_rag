import os
import chromadb
import ollama

DATA_PATH = os.path.join('data','scriptures.txt')
EMBEDDINGS_MODEL = 'nomic-embed-text'
CHROMA_PATH = "chroma_dir"
COLLECTION_NAME = "verses"
NUM_VERSES_IN_DOC = 4

def parse_scriptures(fp):
    """Get each verse in the scriptures"""
    documents = []
    ids = []
    file = open(fp, 'r')
    current_document_set = []
    current_ids_set = []
    for line in file:
        current_id = line.split("     ")[0]
        if (len(current_ids_set) > 0) and (current_ids_set[-1].split(":")[0] != current_id.split(":")[0]): ## We got to a new book, no need to combine verses
            current_document_set = []
            current_ids_set = []
        current_document_set.append(line.split("     ")[1])
        current_ids_set.append(current_id)

        
        if len(current_document_set) == NUM_VERSES_IN_DOC:
            documents.append("\n".join(current_document_set))
            ids.append(current_ids_set[0] + "-" + current_ids_set[-1].split(":")[1])
            current_ids_set.pop(0)
            current_document_set.pop(0)
            

    return (documents, ids)


def get_chroma_collection(chroma_path):
    """Get the relevant collection"""
    os.makedirs(chroma_path, exist_ok = True)
    ## Initialize the chroma client
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    ## Get the collection name
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return collection

def add_to_collection(documents, ids, collection):
    """Create embeddings for any documents that aren't already in the collection"""
    # Initialize the Ollama client
    client = ollama.Client()

    # Generate embeddings
    embeddings = []
    ids_to_add = []
    documents_to_add = []
    for i, doc in enumerate(documents):
        if len(collection.get(ids[i])['ids']) > 0:
            continue ## No need to get embeddings because we already have them stored. 
        response = client.embeddings(model=EMBEDDINGS_MODEL, prompt=doc)
        collection.add(ids = [ids[i]],
                        embeddings = [response["embedding"]],
                       documents = [doc])
        


def main():
    documents, ids = parse_scriptures(DATA_PATH)
    collection = get_chroma_collection(CHROMA_PATH)
    add_to_collection(documents, ids, collection)

if __name__ == "__main__":
    main()
