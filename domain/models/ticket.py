from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
import uuid

class Status(Enum):
    OPEN = "open";
    IN_PROGRESS = "in_progress";
    DONE = "done";
    CANCELED = "canceled";

class Priority(Enum):
    LOW = "low";
    MEDIUM = "medium";
    HIGH = "high";
    Critical = "critical";

@dataclass
class Ticket:
    title: str
    description: str
    status: Status = Status.OPEN;
    priority: Priority = Priority.MEDIUM;
    tags: List[str] = field(default_factory=list);
    id: str = field(default_factory=lambda: str(uuid.uuid4()));
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self._validate_title()
        self._validate_description()

    def _validate_title(self):
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title cannot be longer than 200 characters")

    def _validate_description(self):
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Ticket:
        try:
            status = Status(data["status"])
        except ValueError:
            raise ValueError(f"Invalid status: '{data['status']}'")

        try:
            priority = Priority(data["priority"])
        except ValueError:
            raise ValueError(f"Invalid priority: '{data['priority']}'")

        ticket = cls.__new__(cls)
        ticket.id = data["id"]
        ticket.title = data["title"]
        ticket.description = data["description"]
        ticket.status = status
        ticket.priority = priority
        ticket.tags = data["tags"]
        created_at_val = data["created_at"]
        if isinstance(created_at_val, str):
            ticket.created_at = datetime.fromisoformat(created_at_val)
        else:
            ticket.created_at = created_at_val
        return ticket