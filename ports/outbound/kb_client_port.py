from abc import ABC, abstractmethod
from typing import List
from xml.dom.minidom import Document


class KBClientPort(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int) -> List[Document]:
        pass

    @abstractmethod
    def list(self, node_path: str, limit: int) -> List[Document]:
        pass

    @abstractmethod
    def retrieve(self, doc_id: str) -> Document:
        pass

    @abstractmethod
    def add(self, doc: Document) -> Document:
        pass