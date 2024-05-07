import unittest

from protobase import Object, traits


class TraitMethodTest(unittest.TestCase):
    class A(Object):
        a: int = 1

    class B(A):
        b: int = 2

    class C(B):
        c: int = 3

    def test_trait_method_dispatch(self):
        self.C(a=1, b=2, c=3)
        self.A(a=1)
        self.B(a=1, b=2)
