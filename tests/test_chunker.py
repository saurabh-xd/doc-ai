"""Unit tests for predictable RAG chunk boundaries."""

import unittest

from app.rag.ingestion.chunker import recursive_chunk_text


class ChunkerTests(unittest.TestCase):
    def test_chunks_respect_size_and_overlap(self):
        chunks = recursive_chunk_text("A" * 600, chunk_size=500, overlap=50)

        self.assertEqual([len(chunk) for chunk in chunks], [500, 150])
        self.assertEqual(chunks[0][-50:], chunks[1][:50])

    def test_blank_text_creates_no_chunks(self):
        self.assertEqual(recursive_chunk_text("   "), [])
