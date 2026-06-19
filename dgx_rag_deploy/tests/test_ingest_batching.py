import unittest
import sys
import types
from unittest.mock import patch

# The local lightweight test environment does not install every optional RAG
# dependency. Production imports the real mmh3 package from requirements.txt.
sys.modules.setdefault("mmh3", types.SimpleNamespace(hash=lambda value, signed=False: hash(value)))

import rag_service


def _chunks(count):
    return [
        {
            "text": f"chunk {index}",
            "section": "Document",
            "content_type": "paragraph",
        }
        for index in range(count)
    ]


class FakeQdrantClient:
    def __init__(self, fail_on_upsert=None):
        self.upserts = []
        self.fail_on_upsert = fail_on_upsert

    def upsert(self, collection_name, points):
        self.upserts.append((collection_name, points))
        if self.fail_on_upsert == len(self.upserts):
            raise RuntimeError("simulated Qdrant failure")


class IngestBatchingTests(unittest.TestCase):
    def _run_ingest(self, client, count):
        self.delete_calls = []

        with (
            patch.object(rag_service, "chunk_markdown_structural", return_value=_chunks(count)),
            patch.object(rag_service, "_embed_batch", side_effect=lambda texts: [[0.1, 0.2] for _ in texts]),
            patch.object(rag_service, "_qclient", return_value=client),
            patch.object(rag_service, "ensure_collection"),
            patch.object(rag_service, "ensure_indexes"),
            patch.object(rag_service, "delete_document_chunks", side_effect=lambda *args: self.delete_calls.append(args) or 0),
            patch.object(rag_service, "RAG_UPSERT_BATCH_SIZE", 2),
        ):
            result = rag_service._do_ingest("large.pdf", "markdown", "test_collection", 1200, {}, "missing-key")
        return result

    def test_large_document_uses_bounded_upserts(self):
        client = FakeQdrantClient()
        result = self._run_ingest(client, 5)

        self.assertEqual(result["chunks"], 5)
        self.assertEqual(result["ingest_batches"], 3)
        self.assertEqual([len(points) for _, points in client.upserts], [2, 2, 1])
        self.assertEqual(
            [point.payload["chunk_index"] for _, points in client.upserts for point in points],
            [0, 1, 2, 3, 4],
        )
        self.assertEqual(len(self.delete_calls), 1)

    def test_failed_later_batch_removes_partial_document(self):
        client = FakeQdrantClient(fail_on_upsert=2)

        with self.assertRaisesRegex(RuntimeError, "Qdrant upsert failed for batch 2/3"):
            self._run_ingest(client, 5)
        self.assertEqual(len(self.delete_calls), 2)


if __name__ == "__main__":
    unittest.main()
