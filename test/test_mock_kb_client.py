import unittest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from domain.models.document import Document
from adapters.secondary.mock_kb_client import MockKBClient


class TestMockKBClientSearch(unittest.TestCase):
    """search() — tìm document theo query"""

    def setUp(self):
        self.client = MockKBClient()

    def test_search_returns_list(self):
        results = self.client.search("email", top_k=5)
        self.assertIsInstance(results, list)

    def test_search_returns_matching_documents(self):
        results = self.client.search("email", top_k=5)
        self.assertGreater(len(results), 0)
        for doc in results:
            self.assertIsInstance(doc, Document)

    def test_search_respects_top_k(self):
        results = self.client.search("email", top_k=1)
        self.assertLessEqual(len(results), 1)

    def test_search_with_no_match_returns_empty_list(self):
        results = self.client.search("xyznotexist", top_k=5)
        self.assertEqual(results, [])

    def test_search_is_case_insensitive(self):
        results_lower = self.client.search("email", top_k=5)
        results_upper = self.client.search("EMAIL", top_k=5)
        self.assertEqual(len(results_lower), len(results_upper))


class TestMockKBClientList(unittest.TestCase):
    """list() — liệt kê document theo node_path"""

    def setUp(self):
        self.client = MockKBClient()

    def test_list_returns_list(self):
        results = self.client.list(node_path="/templates/email", limit=10)
        self.assertIsInstance(results, list)

    def test_list_returns_docs_in_node(self):
        results = self.client.list(node_path="/templates/email", limit=10)
        for doc in results:
            self.assertEqual(doc.node_path, "/templates/email")

    def test_list_respects_limit(self):
        results = self.client.list(node_path="/templates/email", limit=1)
        self.assertLessEqual(len(results), 1)

    def test_list_unknown_node_returns_empty_list(self):
        results = self.client.list(node_path="/unknown/path", limit=10)
        self.assertEqual(results, [])


class TestMockKBClientRetrieve(unittest.TestCase):
    """retrieve() — lấy document theo id"""

    def setUp(self):
        self.client = MockKBClient()

    def test_retrieve_returns_document(self):
        docs = self.client.list(node_path="/templates/email", limit=10)
        doc_id = docs[0].id
        result = self.client.retrieve(doc_id)
        self.assertIsInstance(result, Document)
        self.assertEqual(result.id, doc_id)

    def test_retrieve_returns_correct_document(self):
        docs = self.client.list(node_path="/templates/email", limit=10)
        original = docs[0]
        retrieved = self.client.retrieve(original.id)
        self.assertEqual(retrieved.title, original.title)
        self.assertEqual(retrieved.content, original.content)

    def test_retrieve_nonexistent_id_raises_error(self):
        with self.assertRaises(KeyError):
            self.client.retrieve("nonexistent-id")


class TestMockKBClientAdd(unittest.TestCase):
    """add() — thêm document mới"""

    def setUp(self):
        self.client = MockKBClient()

    def test_add_returns_document(self):
        doc = Document(
            title="New Template",
            content="Hello world",
            node_path="/templates/sms",
            tags=["sms"],
        )
        result = self.client.add(doc)
        self.assertIsInstance(result, Document)

    def test_add_document_can_be_retrieved(self):
        doc = Document(
            title="New Template",
            content="Hello world",
            node_path="/templates/sms",
        )
        added = self.client.add(doc)
        retrieved = self.client.retrieve(added.id)
        self.assertEqual(retrieved.title, "New Template")

    def test_add_document_appears_in_list(self):
        doc = Document(
            title="New Template",
            content="Hello world",
            node_path="/templates/sms",
        )
        self.client.add(doc)
        results = self.client.list(node_path="/templates/sms", limit=10)
        titles = [d.title for d in results]
        self.assertIn("New Template", titles)

    def test_add_document_appears_in_search(self):
        doc = Document(
            title="Unique SMS Template",
            content="unique content here",
            node_path="/templates/sms",
        )
        self.client.add(doc)
        results = self.client.search("unique", top_k=5)
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()