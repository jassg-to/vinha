"""Minimal in-memory Firestore fake for testing.

Supports the subset of the AsyncClient API used by our repository layer:
  db.collection(name).document([id]).get/set/update/delete
  db.collection(name).order_by(...).where(...).stream()
  db.collection(name).document(id).collection(sub).document(...)...
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field


@dataclass
class FakeDocSnapshot:
    id: str
    _data: dict | None
    exists: bool

    def to_dict(self) -> dict | None:
        return copy.deepcopy(self._data) if self._data else None


class FakeDocRef:
    def __init__(self, collection: FakeCollection, doc_id: str):
        self._collection = collection
        self.id = doc_id

    async def get(self) -> FakeDocSnapshot:
        data = self._collection._docs.get(self.id)
        return FakeDocSnapshot(
            id=self.id,
            _data=copy.deepcopy(data) if data else None,
            exists=data is not None,
        )

    async def set(self, data: dict) -> None:
        self._collection._docs[self.id] = copy.deepcopy(data)

    async def update(self, updates: dict) -> None:
        if self.id not in self._collection._docs:
            raise Exception(f"Document {self.id} does not exist")
        self._collection._docs[self.id].update(copy.deepcopy(updates))

    async def delete(self) -> None:
        self._collection._docs.pop(self.id, None)

    def collection(self, name: str) -> FakeCollection:
        key = f"{self._collection._path}/{self.id}/{name}"
        return self._collection._db._get_collection(key)


class FakeQuery:
    def __init__(self, collection: FakeCollection):
        self._collection = collection
        self._order_field: str | None = None
        self._order_dir: str = "ASCENDING"
        self._filters: list[tuple[str, str, object]] = []
        self._limit: int | None = None

    def order_by(self, field_name: str, direction: str = "ASCENDING") -> FakeQuery:
        self._order_field = field_name
        self._order_dir = direction
        return self

    def where(self, field_name: str, op: str, value: object) -> FakeQuery:
        self._filters.append((field_name, op, value))
        return self

    def limit(self, count: int) -> FakeQuery:
        self._limit = count
        return self

    async def stream(self):
        docs = list(self._collection._docs.items())
        for field_name, op, value in self._filters:
            if op == "==":
                docs = [(k, v) for k, v in docs if v.get(field_name) == value]
        if self._order_field:
            reverse = self._order_dir == "DESCENDING"
            docs.sort(key=lambda x: x[1].get(self._order_field, ""), reverse=reverse)
        if self._limit:
            docs = docs[: self._limit]
        for doc_id, data in docs:
            yield FakeDocSnapshot(id=doc_id, _data=copy.deepcopy(data), exists=True)


@dataclass
class FakeCollection:
    _db: FakeFirestore
    _path: str
    _docs: dict[str, dict] = field(default_factory=dict)

    def document(self, doc_id: str | None = None) -> FakeDocRef:
        if doc_id is None:
            doc_id = uuid.uuid4().hex[:20]
        return FakeDocRef(self, doc_id)

    def order_by(self, field_name: str, direction: str = "ASCENDING") -> FakeQuery:
        return FakeQuery(self).order_by(field_name, direction)

    def where(self, field_name: str, op: str, value: object) -> FakeQuery:
        return FakeQuery(self).where(field_name, op, value)

    def limit(self, count: int) -> FakeQuery:
        return FakeQuery(self).limit(count)

    async def stream(self):
        for doc_id, data in list(self._docs.items()):
            yield FakeDocSnapshot(id=doc_id, _data=copy.deepcopy(data), exists=True)


class FakeFirestore:
    def __init__(self):
        self._collections: dict[str, FakeCollection] = {}

    def _get_collection(self, path: str) -> FakeCollection:
        if path not in self._collections:
            self._collections[path] = FakeCollection(_db=self, _path=path)
        return self._collections[path]

    def collection(self, name: str) -> FakeCollection:
        return self._get_collection(name)

    def clear(self) -> None:
        self._collections.clear()
