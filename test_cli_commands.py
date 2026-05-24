import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from click.testing import CliRunner
from adapters.primary.cli.main import cli


class TestCreateCommand(unittest.TestCase):
    """tickets create"""

    def setUp(self):
        self.runner = CliRunner()
        self.test_file = "/tmp/test_cli_tickets.json"
        self.env = {"TICKETS_FILE": self.test_file}

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_create_ticket_successfully(self):
        result = self.runner.invoke(cli, [
            "create", "--title", "Fix bug", "--description", "Something broke"
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("created", result.output.lower())

    def test_create_outputs_ticket_id(self):
        result = self.runner.invoke(cli, [
            "create", "--title", "Fix bug", "--description", "desc"
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("id", result.output.lower())

    def test_create_with_all_options(self):
        result = self.runner.invoke(cli, [
            "create",
            "--title", "Deploy feature",
            "--description", "Deploy to prod",
            "--priority", "high",
            "--tags", "backend,devops",
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("created", result.output.lower())

    def test_create_with_empty_title_shows_error(self):
        result = self.runner.invoke(cli, [
            "create", "--title", "", "--description", "desc"
        ], env=self.env)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.output.lower())


class TestListCommand(unittest.TestCase):
    """tickets list"""

    def setUp(self):
        self.runner = CliRunner()
        self.test_file = "/tmp/test_cli_tickets.json"
        self.env = {"TICKETS_FILE": self.test_file}
        # seed 2 tickets
        self.runner.invoke(cli, ["create", "--title", "Bug A", "--description", "desc", "--priority", "high"], env=self.env)
        self.runner.invoke(cli, ["create", "--title", "Bug B", "--description", "desc", "--priority", "low" ], env=self.env)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_list_shows_all_tickets(self):
        result = self.runner.invoke(cli, ["list"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Bug A", result.output)
        self.assertIn("Bug B", result.output)

    def test_list_empty_shows_no_tickets_message(self):
        os.remove(self.test_file)
        result = self.runner.invoke(cli, ["list"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("no tickets", result.output.lower())

    def test_list_filter_by_status(self):
        result = self.runner.invoke(cli, ["list", "--status", "open"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Bug A", result.output)

    def test_list_filter_by_priority(self):
        result = self.runner.invoke(cli, ["list", "--priority", "high"], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Bug A", result.output)
        self.assertNotIn("Bug B", result.output)


class TestShowCommand(unittest.TestCase):
    """tickets show <id>"""

    def setUp(self):
        self.runner = CliRunner()
        self.test_file = "/tmp/test_cli_tickets.json"
        self.env = {"TICKETS_FILE": self.test_file}
        result = self.runner.invoke(cli, [
            "create",
            "--title", "Fix login",
            "--description", "Login broken",
            "--priority", "critical",
            "--tags", "auth,backend",
        ], env=self.env)
        # extract id from output
        for line in result.output.splitlines():
            if "id" in line.lower():
                self.ticket_id = line.split(":")[-1].strip()
                break

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_show_displays_ticket_detail(self):
        result = self.runner.invoke(cli, ["show", self.ticket_id], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Fix login", result.output)

    def test_show_displays_all_fields(self):
        result = self.runner.invoke(cli, ["show", self.ticket_id], env=self.env)
        self.assertIn("critical", result.output.lower())
        self.assertIn("Login broken", result.output)

    def test_show_displays_tags(self):
        result = self.runner.invoke(cli, ["show", self.ticket_id], env=self.env)
        self.assertIn("auth", result.output)

    def test_show_nonexistent_id_shows_error(self):
        result = self.runner.invoke(cli, ["show", "nonexistent-id"], env=self.env)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not found", result.output.lower())


class TestUpdateCommand(unittest.TestCase):
    """tickets update <id>"""

    def setUp(self):
        self.runner = CliRunner()
        self.test_file = "/tmp/test_cli_tickets.json"
        self.env = {"TICKETS_FILE": self.test_file}
        result = self.runner.invoke(cli, [
            "create", "--title", "Fix bug", "--description", "desc"
        ], env=self.env)
        for line in result.output.splitlines():
            if "id" in line.lower():
                self.ticket_id = line.split(":")[-1].strip()
                break

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_update_status_successfully(self):
        result = self.runner.invoke(cli, [
            "update", self.ticket_id, "--status", "done"
        ], env=self.env)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("updated", result.output.lower())

    def test_update_confirms_new_status(self):
        self.runner.invoke(cli, ["update", self.ticket_id, "--status", "in_progress"], env=self.env)
        result = self.runner.invoke(cli, ["show", self.ticket_id], env=self.env)
        self.assertIn("in_progress", result.output.lower())

    def test_update_nonexistent_id_shows_error(self):
        result = self.runner.invoke(cli, [
            "update", "nonexistent-id", "--status", "done"
        ], env=self.env)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not found", result.output.lower())

    def test_update_with_invalid_status_shows_error(self):
        result = self.runner.invoke(cli, [
            "update", self.ticket_id, "--status", "INVALID"
        ], env=self.env)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.output.lower())


if __name__ == "__main__":
    unittest.main()