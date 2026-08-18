from retriever import retrieve


results = retrieve(
    "what is companys name?"
)

for result in results:

    print("\nScore:", result.score)
    print("Page:", result.metadata["page_number"])
    print("Text:", result.metadata["text"])