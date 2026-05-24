import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from domain.models.ticket import Ticket, Status, Priority
from adapters.secondary.json_storage import JsonStorageAdapter


class TestJsonStorageNormalFlow(unittest.TestCase):

    def setUp(self):
        self.test_file = "/tmp/test_tickets.json"
        self.storage = JsonStorageAdapter(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_creates_file_if_not_exists(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.storage.save(ticket)
        self.assertTrue(os.path.exists(self.test_file))

    def test_save_and_find_by_id_returns_same_ticket(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.storage.save(ticket)
        found = self.storage.find_by_id(ticket.id)
        self.assertEqual(found.id, ticket.id)
        self.assertEqual(found.title, ticket.title)

    def test_find_all_returns_empty_list_when_no_tickets(self):
        self.assertEqual(self.storage.find_all(), [])

    def test_find_all_returns_all_saved_tickets(self):
        self.storage.save(Ticket(title="Bug A", description="desc"))
        self.storage.save(Ticket(title="Bug B", description="desc"))
        self.assertEqual(len(self.storage.find_all()), 2)

    def test_update_changes_ticket_status(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.storage.save(ticket)
        ticket.status = Status.DONE
        self.storage.update(ticket)
        found = self.storage.find_by_id(ticket.id)
        self.assertEqual(found.status, Status.DONE)

    def test_update_preserves_other_fields(self):
        ticket = Ticket(title="Fix bug", description="desc", tags=["api"])
        self.storage.save(ticket)
        ticket.status = Status.IN_PROGRESS
        self.storage.update(ticket)
        found = self.storage.find_by_id(ticket.id)
        self.assertEqual(found.tags, ["api"])
        self.assertEqual(found.title, "Fix bug")

    def test_delete_removes_ticket(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.storage.save(ticket)
        self.storage.delete(ticket.id)
        self.assertEqual(len(self.storage.find_all()), 0)


class TestJsonStorageFilters(unittest.TestCase):

    def setUp(self):
        self.test_file = "/tmp/test_tickets_filter.json"
        self.storage = JsonStorageAdapter(filepath=self.test_file)
        self.storage.save(Ticket(title="Bug A", description="d", status=Status.OPEN,        priority=Priority.HIGH, tags=["api"]))
        self.storage.save(Ticket(title="Bug B", description="d", status=Status.DONE,        priority=Priority.LOW,  tags=["ui"]))
        self.storage.save(Ticket(title="Bug C", description="d", status=Status.IN_PROGRESS, priority=Priority.HIGH, tags=["api", "backend"]))

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_filter_by_status(self):
        result = self.storage.find_all(status=Status.OPEN)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Bug A")

    def test_filter_by_priority(self):
        result = self.storage.find_all(priority=Priority.HIGH)
        self.assertEqual(len(result), 2)

    def test_filter_by_tag(self):
        result = self.storage.find_all(tag="api")
        self.assertEqual(len(result), 2)


class TestJsonStorageErrorCases(unittest.TestCase):

    def setUp(self):
        self.test_file = "/tmp/test_tickets_error.json"
        self.storage = JsonStorageAdapter(filepath=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_find_by_id_raises_error_when_not_found(self):
        with self.assertRaises(KeyError):
            self.storage.find_by_id("nonexistent-id")

    def test_update_raises_error_when_ticket_not_found(self):
        with self.assertRaises(KeyError):
            self.storage.update(Ticket(title="Ghost", description="desc"))

    def test_delete_raises_error_when_ticket_not_found(self):
        with self.assertRaises(KeyError):
            self.storage.delete("nonexistent-id")

    def test_find_all_returns_empty_when_file_missing(self):
        result = self.storage.find_all()
        self.assertEqual(result, [])

    def test_corrupted_json_raises_error(self):
        with open(self.test_file, "w") as f:
            f.write("{ this is not valid json !!!")
        with self.assertRaises(ValueError):
            self.storage.find_all()


if __name__ == "__main__":
    unittest.main()