import json
import os
from typing import List, Optional

from domain.models.ticket import Ticket, Status, Priority
from ports.outbound.storage_port import StoragePort

class JsonStorageAdapter:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def _load(self) -> dict:
        if not os.path.exists(self.filepath):
            return {}
        with open(self.filepath, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                raise ValueError(f"Corrupted JSON file: {self.filepath}")

    def _save_all(self, data: dict) -> None:
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def save(self, ticket: Ticket) -> None:
        data = self._load()
        if ticket.id in data:
            raise ValueError(f"Ticket {ticket.id} already exists")
        data[ticket.id] = ticket.to_dict()
        self._save_all(data)

    def find_by_id(self, ticket_id: str) -> Ticket:
        data = self._load()
        if ticket_id not in data:
            raise ValueError(f"Ticket {ticket_id} not found")
        return Ticket.from_dict(data[ticket_id])

    def find_all(self, status: Optional[Status] = None, priority: Optional[Priority] = None, tag: Optional[str] = None) -> List[Ticket]:
        data = self._load()
        tickets = [Ticket.from_dict(t) for t in data.values()]
        if status:
            tickets = [t for t in tickets if t.status == status]
        if priority:
            tickets = [t for t in tickets if t.priority == priority]
        if tag:
            tickets = [t for t in tickets if tag in t.tags]
        return tickets

    def update(self, ticket: Ticket) -> None:
        data = self._load()
        if ticket.id not in data:
            raise KeyError(f"Ticket {ticket.id} not found")
        data[ticket.id] = ticket.to_dict()
        self._save_all(data)

    def delete(self, ticket_id: str) -> None:
        data = self._load()
        if ticket_id not in data:
            raise KeyError(f"Ticket {ticket_id} not found")
        del data[ticket_id]
        self._save_all(data)
