from embeddings import embed_text

vector = embed_text(
    "Employees receive 18 days of annual leave."
)

print("Dimensions:", len(vector))
print("First 10 values:", vector[:10])