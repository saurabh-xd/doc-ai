import pymupdf


def load_pdf(file_path: str):
    document = pymupdf.open(file_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    document.close()

    return pages