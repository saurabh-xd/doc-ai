import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question: str, context_chunks):

    context = "\n\n".join(
        f"""
[Source {i + 1}]
Document: {chunk["filename"]}
Page: {chunk["page_number"]}

{chunk["text"]}
"""
        for i, chunk in enumerate(context_chunks)
    )

    prompt = f"""
You are an AI document assistant.

Answer the user's question using ONLY the provided sources.

Rules:
- Do not use outside knowledge.
- If the sources do not contain the answer, say you could not find it.
- Do not invent facts.
- Cite the relevant source numbers in your answer.

Sources:

{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt
    )

    for chunk in response:

        if chunk.text:
            yield chunk.text