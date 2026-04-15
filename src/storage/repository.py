from typing import Dict, List


class InMemoryRepository:
    """Temporary repository used before SQLite integration."""

    def __init__(self) -> None:
        self._items: List[Dict[str, str]] = []

    def add(self, item: Dict[str, str]) -> None:
        self._items.append(item)

    def all(self) -> List[Dict[str, str]]:
        return list(self._items)
