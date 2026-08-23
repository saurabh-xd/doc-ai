import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "doc-ai")
_index = None


def get_index():
    """Create the Pinecone index only when a request needs it.

    This keeps imports and the health endpoint available when Pinecone is
    temporarily unreachable.
    """
    global _index

    if _index is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is not configured")

        client = Pinecone(api_key=api_key)
        _index = client.Index(INDEX_NAME)

    return _index
