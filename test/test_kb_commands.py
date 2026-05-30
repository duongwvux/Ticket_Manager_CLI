import unittest
import sys, os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from click.testing import CliRunner
from adapters.primary.cli.main import cli

TMP_DIR = tempfile.gettempdir()


class TestKBSearchCommand(unittest.TestCase):
    """kb search <query>"""

    def setUp(self):
        self.runner = CliRunner()
        self.env = {"KB_CLIENT": "mock"}

    def test_search_returns_results(self):
        result = self.runner.invoke(cli, ["kb", "search", "email"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("email", result.output.lower())

    def test_search_with_top_k_option(self):
        result = self.runner.invoke(cli, ["kb", "search", "email", "--top-k", "1"], env=self.env)
        self.assertEqual(result.exit_code, 0)

    def test_search_no_results_shows_message(self):
        result = self.runner.invoke(cli, ["kb", "search", "xyznotexist"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("no results", result.output.lower())

    def test_search_shows_document_title(self):
        result = self.runner.invoke(cli, ["kb", "search", "email"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertGreater(len(result.output.strip()), 0)


class TestKBListCommand(unittest.TestCase):
    """kb list --node <node_path>"""

    def setUp(self):
        self.runner = CliRunner()
        self.env = {"KB_CLIENT": "mock"}

    def test_list_returns_documents_in_node(self):
        result = self.runner.invoke(cli, [
            "kb", "list", "--node", "/templates/email"
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertGreater(len(result.output.strip()), 0)

    def test_list_with_limit_option(self):
        result = self.runner.invoke(cli, [
            "kb", "list", "--node", "/templates/email", "--limit", "1"
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)

    def test_list_unknown_node_shows_message(self):
        result = self.runner.invoke(cli, [
            "kb", "list", "--node", "/unknown/path"
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("no documents", result.output.lower())

    def test_list_requires_node_option(self):
        result = self.runner.invoke(cli, ["kb", "list"], env=self.env)
        self.assertNotEqual(result.exit_code, 0)


class TestKBRetrieveCommand(unittest.TestCase):
    """kb retrieve <doc_id>"""

    def setUp(self):
        self.runner = CliRunner()
        self.env = {"KB_CLIENT": "mock"}
        # lấy doc_id từ list
        result = self.runner.invoke(cli, [
            "kb", "list", "--node", "/templates/email"
        ], env=self.env)
        # parse id từ dòng đầu output: "[doc-001] Title..."
        first_line = result.output.strip().splitlines()[0]
        self.doc_id = first_line.split("]")[0].replace("[", "").strip()

    def test_retrieve_shows_document_detail(self):
        result = self.runner.invoke(cli, ["kb", "retrieve", self.doc_id], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(self.doc_id, result.output)

    def test_retrieve_shows_title_and_content(self):
        result = self.runner.invoke(cli, ["kb", "retrieve", self.doc_id], env=self.env)
        self.assertIn("title", result.output.lower())
        self.assertIn("content", result.output.lower())

    def test_retrieve_shows_node_path(self):
        result = self.runner.invoke(cli, ["kb", "retrieve", self.doc_id], env=self.env)
        self.assertIn("/templates/email", result.output)

    def test_retrieve_nonexistent_id_shows_error(self):
        result = self.runner.invoke(cli, ["kb", "retrieve", "nonexistent-id"], env=self.env)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not found", result.output.lower())


class TestKBAddCommand(unittest.TestCase):
    """kb add --title --content --path --tags"""

    def setUp(self):
        self.runner = CliRunner()
        self.env = {"KB_CLIENT": "mock"}

    def test_add_document_successfully(self):
        result = self.runner.invoke(cli, [
            "kb", "add",
            "--title", "New Template",
            "--content", "Hello world",
            "--path", "/templates/sms",
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("added", result.output.lower())

    def test_add_outputs_document_id(self):
        result = self.runner.invoke(cli, [
            "kb", "add",
            "--title", "New Template",
            "--content", "Hello world",
            "--path", "/templates/sms",
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("id", result.output.lower())

    def test_add_with_tags(self):
        result = self.runner.invoke(cli, [
            "kb", "add",
            "--title", "SMS Template",
            "--content", "Hello...",
            "--path", "/templates/sms",
            "--tags", "sms,template",
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)

    def test_add_missing_title_shows_error(self):
        result = self.runner.invoke(cli, [
            "kb", "add",
            "--content", "Hello world",
            "--path", "/templates/sms",
        ], env=self.env)
        self.assertNotEqual(result.exit_code, 0)

    def test_add_missing_path_shows_error(self):
        result = self.runner.invoke(cli, [
            "kb", "add",
            "--title", "New Template",
            "--content", "Hello world",
        ], env=self.env)
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()