"""
este modulo implementa la unificacion de primer orden (o unificacion semantica)
"""

from functools import singledispatch

from protobase.traits.zip import Zip


class Unify(Zip):
    """
    Clase que hace a un objeto unificable.
    """

    def __unify__(self, other):
        if not isinstance(other, type(self)):
            return

        solution = Solution()
        for _, (child_self, child_other) in self.zip(other):
            if not (child_uni := unify(child_self, child_other)):
                return
            solution.update(child_uni)

        return solution


class UnificationVar: ...


class Solution: ...


def unify(a, b) -> Solution | None: ...


def reify(a, uni: Solution): ...


@singledispatch
def _unify(q, k):
    raise NotImplementedError()
