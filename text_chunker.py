
def chunk_text(text, chunk_size=500, overlap=50):

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


if __name__ == "__main__":

    sample_text = """
    KNOVIA is an AI-powered project knowledge management platform.
    The database schema has been completed.
    Backend API integration is currently ongoing.
    The frontend dashboard is still pending.
    """

    result = chunk_text(sample_text)

    for i, chunk in enumerate(result):
        print(f"\nChunk {i + 1}:")
        print(chunk)
