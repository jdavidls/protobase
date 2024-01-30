from __future__ import annotations
from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Any, Protocol
from protobase.core import Trait, fields_of


class Transform(Trait):
    def _transform(self, transformer: Transformer) -> dict[str, Any]:
        return {
            field: transformer(child)
            for field in fields_of(type(self))
            if isinstance(child := getattr(self, field), Transform)
        }


class Transformer[T](Protocol):
    def __call__(self, obj: Transform) -> T:
        ...


class TreeTransformer(ABC):
    def __call__(self, obj: Transform):
        return self._transform(obj, **obj._transform(self))

    @abstractmethod
    def _transform(self, obj: Transform, /, **items) -> Any:
        ...


class GraphTransformer(ABC):
    def __init__(self):
        self._visited = dict[Transform, Any] = {}

    def __call__(self, obj: Transform):
        if obj in self._visited:
            return self._visited[obj]

        return self._transform(obj, **obj._transform(self))

    @abstractmethod
    def _transform(self, obj: Transform, /, **items) -> Any:
        ...
