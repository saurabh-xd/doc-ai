"""Unit test retrieval without contacting Gemini or Pinecone."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.rag.retrieval.retriever import retrieve


class RetrievalTests(unittest.TestCase):
    @patch("app.rag.retrieval.retriever.get_index")
    @patch("app.rag.retrieval.retriever.embed_texts")
    def test_retrieve_filters_by_user(self, mock_embed, mock_get_index):
        mock_embed.return_value = [[0.1, 0.2]]
        index = Mock()
        index.query.return_value = SimpleNamespace(matches=["matching-chunk"])
        mock_get_index.return_value = index

        matches = retrieve("leave policy", user_id="user-123", top_k=3)

        self.assertEqual(matches, ["matching-chunk"])
        self.assertEqual(
            index.query.call_args.kwargs["filter"],
            {"user_id": {"$eq": "user-123"}},
        )
