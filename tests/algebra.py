from __future__ import annotations
from typing import TypeAlias

from pathlib import Path

import lark

from protobase import Obj, traits
from protobase.core import fields_of


class AST(*traits.Common):
    @classmethod
    def builder(cls, **kwargs):
        fields = dict(fields_of(cls))
        for kw in kwargs:
            fields.pop(kw)
        return lambda _, children: cls(**dict(zip(fields, children)), **kwargs)


class Add(Obj, AST):
    l: Node
    r: Node

    def __str__(self):
        return f"{self.l} + {self.r}"


class Sub(Obj, AST):
    l: Node
    r: Node

    def __str__(self):
        return f"{self.l} - {self.r}"


class Mul(Obj, AST):
    l: Node
    r: Node

    def __str__(self):
        l = f"({self.l})" if isinstance(self.l, (Add, Sub)) else str(self.l)
        r = f"({self.r})" if isinstance(self.r, (Add, Sub)) else str(self.r)
        return f"{l} * {r}"


class Div(Obj, AST):
    l: Node
    r: Node

    def __str__(self):
        l = f"({self.l})" if isinstance(self.l, (Add, Sub)) else str(self.l)
        r = f"({self.r})" if isinstance(self.r, (Add, Sub)) else str(self.r)
        return f"{l} / {r}"


class Neg(Obj, AST):
    r: Node

    def __str__(self):
        return f"-{self.r}"


Node: TypeAlias = float | str | Neg | Add | Sub | Mul | Div


class Algebra:
    class SyntaxTreeBuilder(lark.Transformer):
        """Builds a syntax tree from a Lark parse tree."""

        # identifiers
        def id(self, children):
            return str(children[0].value)

        # literals
        def nat(self, children):
            return float(children[0].value)

        # containers
        def parens(self, children) -> Node:
            return children[0]

        # operators
        add = Add.builder()
        sub = Sub.builder()
        mul = Mul.builder()
        div = Div.builder()
        neg = Neg.builder()

    def __init__(self):
        with (Path(__file__).parent / "algebra.lark").open() as grammar_file:
            self.lark = lark.Lark(
                grammar_file,
                start="expr",
                strict=True,
                parser="lalr",
                transformer=self.SyntaxTreeBuilder(),
                # import_paths=[str(path) for path in self.GRAMMAR_IMPORT_PATHS],
            )

    def parse(self, text: str) -> Node:
        return self.lark.parse(text)


expr = Algebra().parse
