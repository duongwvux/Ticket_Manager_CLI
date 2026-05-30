from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from itertools import count
import uuid

id_counter = count(start=1)

def  generate_id() -> str:
    return f"doc-{next(id_counter):03d}"

@dataclass
class Document:
    id = str(field(default=generate_id))
    title: str
    content: str
    node_path: str
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        self._validate_title()
        self._validate_content()
        self._validate_node_path()

    def _validate_title(self):
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

    def _validate_content(self):
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")

    def _validate_node_path(self):
        if not self.node_path or not self.node_path.strip():
            raise ValueError("Node path cannot be empty")
        if not self.node_path.startswith("/"):
            raise ValueError("Node path must start with '/'")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "node_path": self.node_path,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, doc: dict) -> Document:
        return cls(
            id = doc['id'],
            title = doc['title'],
            content = doc['content'],
            node_path = doc['node_path'],
            tags = doc.get('tags', []),
        )