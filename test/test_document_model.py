import unittest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from domain.models.document import Document


class TestDocumentCreation(unittest.TestCase):
    """Normal flow: tạo document hợp lệ"""

    def test_create_with_required_fields(self):
        doc = Document(
            title="Customer Response Template",
            content="Dear customer...",
            node_path="/templates/email",
        )
        self.assertEqual(doc.title, "Customer Response Template")
        self.assertEqual(doc.content, "Dear customer...")
        self.assertEqual(doc.node_path, "/templates/email")

    def test_has_auto_generated_id(self):
        doc = Document(title="Doc A", content="content", node_path="/docs")
        self.assertIsNotNone(doc.id)
        self.assertGreater(len(doc.id), 0)

    def test_two_documents_have_different_ids(self):
        d1 = Document(title="Doc A", content="content", node_path="/docs")
        d2 = Document(title="Doc B", content="content", node_path="/docs")
        self.assertNotEqual(d1.id, d2.id)

    def test_default_tags_is_empty_list(self):
        doc = Document(title="Doc A", content="content", node_path="/docs")
        self.assertEqual(doc.tags, [])

    def test_create_with_all_fields(self):
        doc = Document(
            id="doc-001",
            title="Email Template",
            content="Hello...",
            node_path="/templates/email",
            tags=["template", "email"],
        )
        self.assertEqual(doc.id, "doc-001")
        self.assertEqual(doc.tags, ["template", "email"])


class TestDocumentValidation(unittest.TestCase):
    """Invalid input: validation rules"""

    def test_empty_title_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Document(title="", content="content", node_path="/docs")
        self.assertIn("title", str(ctx.exception).lower())

    def test_empty_content_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Document(title="Doc A", content="", node_path="/docs")
        self.assertIn("content", str(ctx.exception).lower())

    def test_empty_node_path_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Document(title="Doc A", content="content", node_path="")
        self.assertIn("node_path", str(ctx.exception).lower())

    def test_node_path_must_start_with_slash(self):
        with self.assertRaises(ValueError) as ctx:
            Document(title="Doc A", content="content", node_path="docs/guides")
        self.assertIn("node_path", str(ctx.exception).lower())


class TestDocumentSerialization(unittest.TestCase):
    """to_dict / from_dict"""

    def test_to_dict_contains_all_fields(self):
        doc = Document(
            id="doc-001",
            title="Email Template",
            content="Hello...",
            node_path="/templates/email",
            tags=["template"],
        )
        d = doc.to_dict()
        self.assertEqual(d["id"], "doc-001")
        self.assertEqual(d["title"], "Email Template")
        self.assertEqual(d["content"], "Hello...")
        self.assertEqual(d["node_path"], "/templates/email")
        self.assertEqual(d["tags"], ["template"])

    def test_from_dict_restores_document(self):
        original = Document(
            id="doc-001",
            title="Email Template",
            content="Hello...",
            node_path="/templates/email",
            tags=["template"],
        )
        restored = Document.from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.title, original.title)
        self.assertEqual(restored.content, original.content)
        self.assertEqual(restored.node_path, original.node_path)
        self.assertEqual(restored.tags, original.tags)

    def test_from_dict_missing_required_field_raises_error(self):
        with self.assertRaises((ValueError, KeyError)):
            Document.from_dict({"id": "doc-001", "title": "Doc"})


if __name__ == "__main__":
    unittest.main()