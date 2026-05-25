from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.ticket import Ticket, Status, Priority


class StoragePort(ABC):

    @abstractmethod
    def save(self, ticket: Ticket) -> None:
        pass

    @abstractmethod
    def find_by_id(self, ticket_id: str) -> Ticket:
        pass

    @abstractmethod
    def find_all(self, status: Optional[Status] = None, priority: Optional[Priority] = None, tag: Optional[str] = None) -> List[Ticket]:
        pass

    @abstractmethod
    def update(self, ticket: Ticket) -> None:
        pass

    @abstractmethod
    def delete(self, ticket_id: str) -> None:
        pass