import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def rewrite_query(question: str) -> str:

    prompt = f"""
Rewrite the following user question into a clear,
self-contained search query for a document retrieval system.

Keep the original meaning.
Do not answer the question.
Return only the rewritten query.

User question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()