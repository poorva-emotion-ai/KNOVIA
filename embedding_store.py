
import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# ==========================================
# CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path="./knovia_db"
)

collection = client.get_or_create_collection(
    name="knovia_documents"
)


# ==========================================
# STORE DOCUMENT CHUNKS
# ==========================================

def store_chunks(chunks, project_id, source_name, document_id):

    if not chunks:
        raise ValueError("No chunks available to store.")

    project_id = int(project_id)
    document_id = int(document_id)

    # Generate embeddings
    embeddings = model.encode(
        chunks,
        show_progress_bar=False
    ).tolist()

    # Create unique IDs for every chunk
    ids = [
        f"project_{project_id}_document_{document_id}_chunk_{i}"
        for i in range(len(chunks))
    ]

    # Store metadata
    metadatas = [
        {
            "project_id": project_id,
            "document_id": document_id,
            "source": str(source_name),
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    # Store in ChromaDB
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Successfully stored {len(chunks)} chunks "
        f"from {source_name}!"
    )

    return document_id


# ==========================================
# LIST PROJECT DOCUMENTS
# ==========================================

def list_documents(project_id):

    results = collection.get(
        where={"project_id": int(project_id)},
        include=["metadatas"]
    )

    documents = {}

    for metadata in results["metadatas"]:

        document_id = metadata["document_id"]

        if document_id not in documents:

            documents[document_id] = {
                "document_id": document_id,
                "source": metadata["source"],
                "chunk_count": 0
            }

        documents[document_id]["chunk_count"] += 1

    return list(documents.values())


# ==========================================
# DELETE DOCUMENT
# ==========================================

def delete_document(document_id):

    document_id = int(document_id)

    results = collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    if not results["ids"]:
        print("Document not found.")
        return False

    collection.delete(
        where={"document_id": document_id}
    )

    print("Document chunks deleted successfully!")

    return True
