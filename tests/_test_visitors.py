from __future__ import annotations
from functools import singledispatch
from typing import Callable, MappingView

import unittest

from protobase.traits.zip import Zip
from protobase.visit.transform import TreeTransformer
from tests.algebra import Node, expr


## la variable debe implementar el patron criteria, una variable captura
## una expresion, y la variable se puede reemplazar por cualquier expresion
## que cumpla con el patron criteria


class UnificationVar:
    ...


class Unification[T]:
    vars: dict[Unifier, set[T]]

    def update(self, other: Unification):
        for var, values in other.vars.items():
            if var not in self.vars:
                self.vars[var] = values
            else:
                self.vars[var].update(values)


class Unifier:
    """
    Una variable de unificacion
    """


@singledispatch
def syntactic_unifier(q, k):
    raise NotImplementedError()


@syntactic_unifier.register
def tuple_unifier(q: tuple | list, k):
    if not isinstance(k, type(q)):
        return False

    if len(q) != len(k):
        return False

    unification = Unification()

    for self_child, other_child in zip(q, k):
        if not (uni_child := unify(self_child, other_child)):
            return False
        unification.update(uni_child)

    return unification


type Unification[T] = dict[Unifier, set[T]]


def unify(Q: T, K: T) -> Unification | None:
    unification = {}

    def _unify(q, k):
        if isinstance(q, Unifier):  # Equational
            if q not in unification:
                unification[q] = set(k)
            else:
                unification[q].add(k)

            # q actua como capturador de variable, puede aparecer varias veces en Q

        q_cls = type(q)
        if issubclass(q_cls, Unify):
            # syntactical matching
            if not isinstance(k, q_cls):
                return False

            # unifica dos estructuras conocidas, k deriva de q
            for _, (qs, ks) in q.zip(k):
                _unify(qs, ks)
        else:
            return syntactic_unifier(q, k)

    if _unify(Q, K) is True:
        return unification


# def unify[
#     V, P, T
# ](pattern: P, target: T, /, unification: Iterable[V]) -> dict[V, set[T]] | None:
#     unification = {var: set() for var in unification}

#     def _unify(pattern: Node, target: Node) -> bool:
#         if pattern in unification:
#             unification[pattern].add(target)
#             return True

#         cls = type(pattern)

#         if not isinstance(target, cls):
#             return False

#         if not isinstance(cls, Zip):
#             return pattern == target

#         for _attr, (subpat, subnod) in pattern.zip(target):
#             if _unify(subpat, subnod) is False:
#                 return False

#         return True

#     return unification if _unify(pattern, target) is True else None


def reify[V, T](action: T, /, vars: MappingView[V, T]):
    def _reify(action: Node):
        if action in vars:  # is_var
            return vars[action]

        if not isinstance(action, Zip):
            return action

        cls = type(action)
        return cls(**{attr: _reify(subact) for attr, (subact) in action.zip()})

    return _reify(action)


def transform[
    T, R
](node: T, transformer: Callable[[T], R], /, avoid_circularity=True) -> T:
    visited = {}

    def _transform(node):
        if node in visited:
            return visited[node]

        if isinstance(node, Zip):
            result = transformer(
                node, **{attr: _transform(subnode) for attr, (subnode) in node.zip()}
            )
        else:
            result = transformer(node)

        visited[node] = result
        return result

    return _transform(node)


def traverse[T](node, visitor):
    def _eval(node: T):
        with visitor(node) as visit:
            if isinstance(node, Zip):
                node = visit(node, **{nm: _eval(sn) for nm, sn in node.zip()})
            else:
                node = visit(node)

        return node

    return _eval(node)


type UnifyVar = str
type PatternVarsAction = tuple[Node, set[UnifyVar], Node]


class Transformer(TreeTransformer):
    rules: list[PatternVarsAction] = []

    def transform(self, node: Node, /, **kwargs) -> Node:
        for pattern, vars, action in self.rules:
            if (uni := unify(pattern, node, unification=vars)) is not None:
                node = reify(action, vars=uni)

        return node


class TestTransform(unittest.TestCase):
    RULES = [
        (
            expr("(a+b) * (a+b)"),
            {"a", "b"},
            expr("a*a + 2*a*b + b*b"),
        ),
        (
            expr("(a-b) * (a-b)"),
            {"a", "b"},
            expr("a*a - 2*a*b + b*b"),
        ),
        (
            expr("(a+b) * (a-b)"),
            {"a", "b"},
            expr("a*a + b*b"),
        ),
    ]

    def test_all(self):
        ...
        print(expr("a*a + 2*a*b + b*b"))
        print(
            expr("(a+b) * (a+b)"),
        )
