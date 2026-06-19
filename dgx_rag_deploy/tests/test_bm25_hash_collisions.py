import sys
import types
import unittest
from unittest.mock import patch

# The lightweight local test environment does not install every optional RAG
# dependency. Production imports the real mmh3 package from requirements.txt.
sys.modules.setdefault("mmh3", types.SimpleNamespace(hash=lambda value, signed=False: hash(value)))

from modules import qdrant_ops


class Bm25HashCollisionTests(unittest.TestCase):
    def test_colliding_terms_share_one_sparse_index(self):
        with patch.object(qdrant_ops.mmh3, "hash", return_value=17):
            vector = qdrant_ops.tokenize_bm25("alpha beta beta")

        self.assertEqual(vector.indices, [17])
        self.assertEqual(vector.values, [3.0])

    def test_sparse_indices_are_sorted_and_unique(self):
        def fake_hash(word, signed=False):
            return {"alpha": 9, "beta": 2, "gamma": 9}[word]

        with patch.object(qdrant_ops.mmh3, "hash", side_effect=fake_hash):
            vector = qdrant_ops.tokenize_bm25("alpha beta gamma")

        self.assertEqual(vector.indices, [2, 9])
        self.assertEqual(vector.values, [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
