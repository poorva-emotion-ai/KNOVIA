import shutil
from pathlib import Path
from pypdf import PdfReader
from docx import Document

from db_operations import add_document


# Document storage location
UPLOAD_FOLDER = Path("data/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def extract_pdf_text(file_path):

    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_docx_text(file_path):

    document = Document(file_path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    )

    return text


def process_document(project_id, source_path):

    source_path = Path(source_path)

    if not source_path.exists():
        raise FileNotFoundError("Document not found.")

    extension = source_path.suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise ValueError("Only PDF and DOCX files are supported.")

    # Create a unique filename
    destination = UPLOAD_FOLDER / source_path.name

    counter = 1

    while destination.exists():
        destination = UPLOAD_FOLDER / (
            f"{source_path.stem}_{counter}{source_path.suffix}"
        )
        counter += 1

    # Copy document into KNOVIA
    shutil.copy2(source_path, destination)

    # Extract document text
    if extension == ".pdf":
        extracted_text = extract_pdf_text(destination)

    else:
        extracted_text = extract_docx_text(destination)

    if not extracted_text.strip():
        destination.unlink(missing_ok=True)
        raise ValueError(
            "No readable text found. The PDF may be scanned or image-based."
        )

    # Save document details in SQLite
    document_id = add_document(
        project_id,
        destination.name,
        str(destination)
    )

    return {
        "document_id": document_id,
        "file_name": destination.name,
        "file_path": str(destination),
        "extracted_text": extracted_text
    }