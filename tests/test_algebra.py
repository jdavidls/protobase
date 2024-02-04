import unittest
from tests.algebra import Add, Mul, Neg, expr


class TestAlgebra(unittest.TestCase):
    def test_algebra_parser(self):
        self.assertEqual(expr("2*a+-b"), Add(l=Mul(l=2.0, r="a"), r=Neg(r="b")))
