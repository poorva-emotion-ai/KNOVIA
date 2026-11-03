import os
import time
from pathlib import Path
import streamlit as st

from document_processor import process_document
from text_chunker import chunk_text
from embedding_store import store_chunks
from retriever import retrieve_chunks

from dotenv import load_dotenv
from google import genai


# ==========================================
# GEMINI CONFIGURATION
# ==========================================

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(dotenv_path=ENV_PATH)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError(
        "Gemini API key not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)


# 2. Project configuration



# 3. Process and store uploaded document
# ==========================================
# PROCESS AND STORE PROJECT DOCUMENT
# ==========================================

def process_and_store_document(project_id, file_path):

    print("\nProcessing document...")

    # 1. Process document using Mahin's backend
    result = process_document(
        project_id,
        file_path
    )

    # 2. Extract document information
    text = result["extracted_text"]

    document_id = result["document_id"]

    source_name = result["file_name"]

    if not text.strip():
        raise ValueError("No readable text found.")

    # 3. Divide text into chunks
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No text chunks generated.")

    # 4. Generate embeddings and store in ChromaDB
    store_chunks(
        chunks,
        project_id=project_id,
        source_name=source_name,
        document_id=document_id
    )

    print("\nDocument processed successfully!")

    print("Project ID:", project_id)
    print("Document ID:", document_id)
    print("File Name:", source_name)
    print("Total Chunks:", len(chunks))

    return {
        "document_id": document_id,
        "project_id": project_id,
        "file_name": source_name,
        "file_path": result["file_path"],
        "chunk_count": len(chunks)
    }


# 4. Validate available source references
def validate_references(context_chunks):

    valid_references = set()

    for chunk in context_chunks:

        reference = (
            chunk["source"],
            chunk["document_id"],
            chunk["chunk_index"]
        )

        valid_references.add(reference)

    return valid_references

def find_matching_references(evidence_quote, context_chunks):
    """
    Find the retrieved chunks containing the exact evidence quote.
    Returns the actual source references from those chunks.
    """

    def normalize_text(text):
        return " ".join(text.split()).casefold()

    normalized_quote = normalize_text(evidence_quote)

    if not normalized_quote:
        return []

    matching_references = []

    for chunk in context_chunks:
        normalized_chunk = normalize_text(chunk["text"])

        if normalized_quote in normalized_chunk:
            matching_references.append({
                "source": chunk["source"],
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"]
            })

    return matching_references

# 5. Generate an answer using retrieved context
def generate_answer(question, project_id, document_ids=None):
    start = time.time()

    # A. Retrieve relevant chunks
    retrieval_start = time.time()

    context_chunks = retrieve_chunks(
    question,
    project_id=project_id,
    document_ids=document_ids
    )

    retrieval_time = time.time() - retrieval_start

    if not context_chunks:
        return "I couldn't find relevant information in the selected documents."

    # B. Display retrieved context
    print("\n--- RETRIEVED CONTEXT ---")

    for i, chunk in enumerate(context_chunks):

        print(f"\nRetrieved Chunk {i + 1}:")
        print("Source:", chunk["source"])
        print("Document ID:", chunk["document_id"])
        print("Chunk Index:", chunk["chunk_index"])
        print("Information:", chunk["text"])

    print("\n--- END OF RETRIEVED CONTEXT ---")

    # C. Build valid reference list
    valid_references = validate_references(context_chunks)

    print("\n--- VALID REFERENCES ---")

    for reference in sorted(valid_references):
        print(reference)

    print("--- END OF REFERENCES ---")

    # D. Prepare context for Gemini
    context = "\n\n".join(
        f"Source: {chunk['source']}\n"
        f"Document ID: {chunk['document_id']}\n"
        f"Chunk Index: {chunk['chunk_index']}\n"
        f"Evidence: {chunk['text']}"
        for chunk in context_chunks
    )



    
    # E. Question-specific prompt

    prompt = f"""
You are KNOVIA, an AI-powered project knowledge management assistant.

Your task is to answer the user's question using the retrieved project documents.

USER QUESTION:
{question}

PROJECT INFORMATION:
{context}

RESPONSE RULES:

1. ANSWER THE ACTUAL QUESTION
- Understand what the user is asking.
- Answer only the specific question or topic requested.
- Do not automatically generate all seven project analysis categories.
- Do not provide unrelated project information.
- If the user asks about knowledge risks, discuss only knowledge risks.
- If the user asks about completed work, discuss only completed work.
- If the user asks for a complete project analysis, cover all seven categories.
- If the user asks a general question about the project, provide a concise relevant answer.

2. PROJECT ANALYSIS CATEGORIES

Use these categories when relevant:
- Completed Work
- Ongoing Work
- Pending Work
- Important Decisions
- Technical Dependencies
- Missing Information
- Knowledge Risks


3. EVIDENCE REQUIREMENTS

For every factual finding:
- Provide supporting evidence from the retrieved documents.
- Quote the exact relevant sentence or passage.
- Copy the evidence word-for-word from the retrieved context.
- Never rewrite or paraphrase the evidence quote.
- If evidence is unavailable, state that the information is not specified.
- Do not generate source filenames, document IDs or chunk indexes.
- Python will attach and validate all source references.


4. KNOWLEDGE RISK ANALYSIS

When the user asks about knowledge risks:
- Identify missing project documentation.
- Identify unclear responsibilities.
- Identify missing backup ownership.
- Identify insufficient progress updates.
- Identify technical dependencies that could block progress.
- Identify possible knowledge-loss risks.
- Distinguish confirmed information gaps from potential consequences.
- Never assume a task has only one responsible person unless supported by evidence.
- Do not present assumptions as confirmed risks.

5. ACCURACY RULES

- Do not invent project details, decisions, responsibilities or progress.
- Do not treat missing documentation as proof that work is incomplete.
- Do not infer deployment status only from missing deployment instructions.
- If information is unavailable, write "Not specified in the documents."
- If evidence supports only a possibility, label it as a potential risk.


6. OUTPUT FORMAT

For each relevant finding, use:

- Finding:
- Evidence:
- Risk Status: Confirmed / Potential / Not applicable

Keep the answer concise, organised and directly relevant to the user's question.
Do not include unrelated categories or lengthy introductions.
If the retrieved documents do not contain enough information to answer,
clearly explain the limitation.

"""

    # F. Generate Gemini response

    gemini_start = time.time()

    response = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    gemini_time = time.time() - gemini_start
    total_time = time.time() - start

    # G. Display execution time

    print(f"\nRetrieval time: {retrieval_time:.2f} seconds")
    print(f"Gemini time: {gemini_time:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")

    return response.output_text


# 6. Member Exit Analysis

def analyze_member_exit(project_id, document_ids, departing_member):

    print(f"\nStarting member exit analysis for {departing_member}...")

    # A. Prepare a question for retrieving member-related information
    question = f"""
    Analyse the project information related to {departing_member}.

    Identify their:
    - Assigned responsibilities
    - Completed work
    - Ongoing work
    - Pending work
    - Technical dependencies
    - Missing documentation
    - Important project contributions

    Use only the available project documents.
    """

    # B. Retrieve relevant project information
    context_chunks = retrieve_chunks(
        question,
        project_id=project_id,
        document_ids=document_ids
    )

    if not context_chunks:
        return "No relevant information found for this member."

    print(f"Retrieved {len(context_chunks)} relevant chunks.")

        # C. Prepare retrieved information for Gemini
    context = "\n\n".join(
        [chunk["text"] for chunk in context_chunks]
    )

    prompt = f"""
    You are KNOVIA, an AI-powered project knowledge and handover assistant.

    Analyse the exit of the following project member:

    Departing Member: {departing_member}

    Use ONLY the project information provided below.

    PROJECT INFORMATION:
    {context}

    Prepare a structured member exit analysis with these sections:

    1. Assigned Responsibilities
    2. Completed Work
    3. Ongoing Work
    4. Pending Work
    5. Technical Dependencies
    6. Missing Documentation or Information
    7. Important Contributions

    IMPORTANT RULES:

    - Use only explicitly documented information.
    - Never assume that a project task belongs to the departing member
    - unless the documents clearly assign it to them.
    - Do not classify a task as completed unless its completion is documented.
    - Do not infer pending API endpoints from general project requirements.
    - Separate individual responsibilities from overall project dependencies.
    - If ownership or task status is unclear, write "Needs human verification".
    - If information is unavailable, write "Not specified".
    - Never invent contributions, responsibilities, or progress.
    - Keep the analysis concise and evidence-based.
    """

    # D. Generate member exit analysis using Gemini
    response = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    return response.output_text

# ==========================================
# STANDALONE RAG TEST
# ==========================================

if __name__ == "__main__":

    project_id = int(input("Enter Project ID: "))

    file_path = input("Enter project document path: ")

    document = process_and_store_document(
        project_id,
        file_path
    )

    document_id = document["document_id"]

    print("\nTesting Member Exit Analysis...")

    exit_analysis = analyze_member_exit(
        project_id=project_id,
        document_ids=[document_id],
        departing_member="Aarav"
    )

    print("\nKNOVIA Member Exit Analysis:")
    print(exit_analysis)

    print("\nKNOVIA is ready to answer questions!")

    while True:

        question = input("\nAsk a question (type 'exit' to stop): ")

        if question.lower().strip() == "exit":
            print("Thank you for using KNOVIA!")
            break

        answer = generate_answer(
            question=question,
            project_id=project_id,
            document_ids=[document_id]
        )

        print("\nKNOVIA Answer:")
        print(answer)
