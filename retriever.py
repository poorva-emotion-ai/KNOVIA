
from embedding_store import collection, model


# ==========================================
# RETRIEVE RELEVANT DOCUMENT CHUNKS
# ==========================================

def retrieve_chunks(
    question,
    project_id,
    top_k=6,
    document_ids=None
):

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    project_id = int(project_id)
    top_k = int(top_k)

    if top_k < 1:
        raise ValueError("top_k must be greater than zero.")

    # Filter by the selected project
    where_filter = {
        "project_id": project_id
    }

    # Optionally filter by selected SQLite document IDs
    if document_ids is not None:

        if not document_ids:
            return []

        document_ids = [int(doc_id) for doc_id in document_ids]

        where_filter = {
            "$and": [
                {"project_id": project_id},
                {"document_id": {"$in": document_ids}}
            ]
        }

    # Count only chunks matching the selected project/document
    matching_records = collection.get(
        where=where_filter,
        include=[]
    )

    matching_count = len(matching_records["ids"])

    if matching_count == 0:
        return []

    # Generate question embedding using the shared model
    question_embedding = model.encode(
        [question],
        show_progress_bar=False
    ).tolist()

    # Retrieve matching chunks
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=min(top_k, matching_count),
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_results = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved_results.append({

            "text": document,

            "source": metadata["source"],

            "document_id": metadata["document_id"],

            "chunk_index": metadata["chunk_index"],

            "distance": distance

        })

    return retrieved_results
