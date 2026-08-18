import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question: str, matches):

    context = "\n\n".join(
        f"[Page {match.metadata['page_number']}]\n"
        f"{match.metadata['text']}"
        for match in matches
    )

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I couldn't find that information in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text