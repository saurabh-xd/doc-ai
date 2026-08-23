import pymupdf


def load_pdf(file_path: str):
    document = pymupdf.open(file_path)

    pages = []  # array of object

    for page_number, page in enumerate(document): #loops through every page
        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    document.close()

    return pages

# [
#     {
#         "page_number": 1,
#         "text": "..."
#     },
#     {
#         "page_number": 2,
#         "text": "..."
#     }
# ]