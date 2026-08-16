from loader import load_pdf
from chunker import chunk_text


pages = load_pdf("data/documents/saurabh_resume.pdf")

for page in pages:

    chunks = chunk_text(page["text"])

    print(f"\n===== Page {page['page_number']} =====")

    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk)