"""
La unificacion compara dos elementos

unify(a, b) -> { Type vars }

para implementar la unificacion se deben despachar los tipos
de los elementos a y b, cuando a y b son del mismo tipo y este implementa
unify se invoca al metooo _unify(self, other)


"""


from typing import Any, Self
from protobase.core import Trait


class Unify(Trait):
    def _unify(self, other: Self):
        ...


class Unificator:
    def __init__(self):
        ...

    def __call__(self, l, r):
        ...


class GraphUnificator:
    def __init__(self):
        self._visited: dict[tuple[Unify, Unify], Any] = {}

    def __call__(self, l, r):
        lr = (l, r)
        if lr in self._visited:
            return self._visited[lr]

        lr_type = (type(l), type(r))

        # dispatch_by_type
