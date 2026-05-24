import unittest
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from domain.models.ticket import Ticket, Status, Priority


class TestTicketCreation(unittest.TestCase):
    """Normal flow: tạo ticket hợp lệ"""

    def test_create_with_required_fields(self):
        ticket = Ticket(title="Fix login bug", description="Users cannot log in")
        self.assertEqual(ticket.title, "Fix login bug")
        self.assertEqual(ticket.description, "Users cannot log in")

    def test_has_auto_generated_id(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.assertIsNotNone(ticket.id)
        self.assertGreater(len(ticket.id), 0)

    def test_two_tickets_have_different_ids(self):
        t1 = Ticket(title="Bug A", description="desc")
        t2 = Ticket(title="Bug B", description="desc")
        self.assertNotEqual(t1.id, t2.id)

    def test_default_status_is_open(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.assertEqual(ticket.status, Status.OPEN)

    def test_default_priority_is_medium(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.assertEqual(ticket.priority, Priority.MEDIUM)

    def test_default_tags_is_empty_list(self):
        ticket = Ticket(title="Fix bug", description="desc")
        self.assertEqual(ticket.tags, [])

    def test_has_created_at_timestamp(self):
        before = datetime.now()
        ticket = Ticket(title="Fix bug", description="desc")
        after = datetime.now()
        self.assertGreaterEqual(ticket.created_at, before)
        self.assertLessEqual(ticket.created_at, after)

    def test_create_with_all_fields(self):
        ticket = Ticket(
            title="Deploy feature",
            description="Deploy to production",
            status=Status.IN_PROGRESS,
            priority=Priority.HIGH,
            tags=["backend", "devops"],
        )
        self.assertEqual(ticket.status, Status.IN_PROGRESS)
        self.assertEqual(ticket.priority, Priority.HIGH)
        self.assertEqual(ticket.tags, ["backend", "devops"])


class TestTicketValidation(unittest.TestCase):
    """Invalid input: validation rules"""

    def test_empty_title_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Ticket(title="", description="desc")
        self.assertIn("title", str(ctx.exception).lower())

    def test_whitespace_title_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Ticket(title="   ", description="desc")
        self.assertIn("title", str(ctx.exception).lower())

    def test_empty_description_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Ticket(title="Fix bug", description="")
        self.assertIn("description", str(ctx.exception).lower())

    def test_title_exceeds_max_length_raises_error(self):
        with self.assertRaises(ValueError) as ctx:
            Ticket(title="x" * 201, description="desc")
        self.assertIn("title", str(ctx.exception).lower())


class TestTicketSerialization(unittest.TestCase):
    """to_dict / from_dict để lưu JSON"""

    def test_to_dict_contains_all_fields(self):
        ticket = Ticket(title="Fix bug", description="desc", tags=["api"])
        d = ticket.to_dict()
        self.assertEqual(d["id"], ticket.id)
        self.assertEqual(d["title"], "Fix bug")
        self.assertEqual(d["description"], "desc")
        self.assertEqual(d["status"], ticket.status.value)
        self.assertEqual(d["priority"], ticket.priority.value)
        self.assertEqual(d["tags"], ["api"])
        self.assertIn("created_at", d)

    def test_from_dict_restores_ticket(self):
        original = Ticket(title="Fix bug", description="desc", tags=["api"])
        restored = Ticket.from_dict(original.to_dict())
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.title, original.title)
        self.assertEqual(restored.status, original.status)
        self.assertEqual(restored.tags, original.tags)

    def test_from_dict_with_invalid_status_raises_error(self):
        data = Ticket(title="Fix bug", description="desc").to_dict()
        data["status"] = "INVALID_STATUS"
        with self.assertRaises(ValueError):
            Ticket.from_dict(data)


if __name__ == "__main__":
    unittest.main()