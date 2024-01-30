# %%
import unittest
import pickle

from protobase.core import Base
from protobase.traits import Eq, Hash, Repr, Init, Consed
from protobase.utils import slots_of


class Simple(Base, Eq, Hash, Repr, Init):
    x: int = 1
    y: int = 2


class Sub(Simple):
    a: int = 99


class Cons(Base, Consed, Repr):
    x: int
    y: int


def pick[T](obj: T) -> T:
    return pickle.loads(pickle.dumps(obj))


class HashTest(unittest.TestCase):
    def test_hash(self):
        a = Simple(x=1, y=2)
        b = Simple(x=1, y=2)

        d = {}
        d[a] = 9
        self.assertEqual(d[b], 9)

    def test_pickle(self):
        a = Simple(x=1, y=2)
        b = pick(a)

        self.assertEqual(a, b)


class ConsignTest(unittest.TestCase):
    def test_consign(self):
        a = Cons(x=1, y=2)
        b = Cons(x=1, y=2)
        c = Cons(x=3, y=4)
        self.assertEqual(a.x, 1)
        self.assertEqual(a.y, 2)
        self.assertIs(a, b)
        self.assertIsNot(a, c)

    def test_pickle(self):
        a = Cons(x=1, y=2)
        b = pick(a)
        self.assertIs(a, b)


# %%
if __name__ == "__main__":
    unittest.main()
