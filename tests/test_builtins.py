# %%
import unittest

from protobase import Base, traits


class InitTest(unittest.TestCase):
    class A(Base, traits.Init):
        a: int = 1

    class B(A):
        b: int = 2

    class C(B):
        c: int = 3

    def test_init_defaults(self):
        c1, c2 = (
            self.C(),
            self.C(a=1, b=2, c=3),
        )
        self.assertEqual(c1.a, 1)
        self.assertEqual(c1.b, 2)
        self.assertEqual(c1.c, 3)

        self.assertEqual(c1.a, c2.a)
        self.assertEqual(c1.b, c2.b)
        self.assertEqual(c1.c, c2.c)


class ReprTest(unittest.TestCase):
    class ABC(Base, traits.Repr, traits.Init):
        a: int = 1
        b: float = 2.0
        c: str = "3"

    def test_repr_default(self):
        a = self.ABC()
        self.assertEqual(repr(a), "ReprTest.ABC()")

    def test_repr(self):
        a = self.ABC(a=2, b=3.0, c="4")
        self.assertEqual(repr(a), "ReprTest.ABC(a=2, b=3.0, c='4')")


class CmpTest(unittest.TestCase):
    class ABC(Base, traits.Repr, traits.Cmp, traits.Eq, traits.Init):
        a: int = 1
        b: float = 2.0
        c: str = "3"

    def test_basic(self):
        x = self.ABC(a=0, b=0.0, c="beta")
        y = self.ABC(a=0, b=0.1, c="alpha")

        self.assertTrue(x < y)
        self.assertFalse(x > y)

    def test_cmp(self):
        items = [
            [
                [
                    self.ABC(a=a, b=b / 10, c=str(c))
                    for c in sorted(["alpha", "beta", "gamma"])
                ]
                for b in range(10)
            ]
            for a in range(10)
        ]

        def indexed_items():
            for i, a in enumerate(items):
                for j, b in enumerate(a):
                    for k, x in enumerate(b):
                        yield (i, j, k), x

        for i1, x in indexed_items():
            for i2, y in indexed_items():
                # print(i1, i2, x, y)
                if i1 == i2:
                    self.assertTrue(x == y)
                    self.assertFalse(x != y)
                    self.assertTrue(x <= y)
                    self.assertTrue(x >= y)
                    self.assertFalse(x < y)
                    self.assertFalse(x > y)
                if i1 < i2:
                    self.assertFalse(x == y)
                    self.assertTrue(x != y)
                    self.assertTrue(x < y)
                    self.assertFalse(x > y)
                    self.assertTrue(x <= y)
                    self.assertFalse(x >= y)
                if i1 > i2:
                    self.assertFalse(x == y)
                    self.assertTrue(x != y)
                    self.assertFalse(x < y)
                    self.assertTrue(x > y)
                    self.assertFalse(x <= y)
                    self.assertTrue(x >= y)

        sorted_items = [i for _, i in indexed_items()]
        resorted = list(sorted(reversed(sorted_items)))
        self.assertEqual(sorted_items, resorted)


class HashTest(unittest.TestCase):
    class ABC(Base, traits.Hash, traits.Eq, traits.Init):
        a: int = 1
        b: float = 2.0
        c: str = "3"

    def test_hash(self):
        a = self.ABC(a=1, b=2.0, c="3")
        b = self.ABC()

        d = {}
        d[a] = 9
        self.assertEqual(d[b], 9)


class InmutableTest(unittest.TestCase):
    class ABC(Base, traits.Inmutable):
        a: int = 1
        b: tuple[frozenset] = frozenset({2.0})

    def test_invalid_inmutable(self):
        class InvalidInmutable(Base, traits.Inmutable):
            dct: dict

        with self.assertRaises(TypeError):
            InvalidInmutable(dct={})

        class InvalidInmutableNested(Base, traits.Inmutable):
            dct: tuple[dict]

        with self.assertRaises(TypeError):
            InvalidInmutableNested(dct=({},))

    def test_inmutable(self):
        a = self.ABC(a=1, b=frozenset({2.0}))

        with self.assertRaises(AttributeError):
            a.a = 2
        with self.assertRaises(AttributeError):
            a.b = frozenset({3.0})


class ConsedTest(unittest.TestCase):
    class Foo(Base, traits.Consed):
        a: int
        b: float
        c: str

    def test_consed(self):
        a = self.Foo(a=1, b=2.0, c="3")
        b = self.Foo(a=1, b=2.0, c="3")

        self.assertIs(a, b)

        c = self.Foo(a=1, b=2.0, c="4")
        self.assertIsNot(a, c)


class ZipTest(unittest.TestCase):
    class Foo(Base, traits.Zip, traits.Init):
        a: int
        b: float
        c: str

    def test_zip(self):
        a = self.Foo(a=1, b=2.0, c="3")
        b = self.Foo(a=9, b=8.0, c="7")

        self.assertEqual(
            list(a.zip(b)),
            [
                ("a", (1, 9)),
                ("b", (2.0, 8.0)),
                ("c", ("3", "7")),
            ],
        )

    def test_zip_raise(self):
        a = self.Foo(a=1, b=2.0, c="3")

        with self.assertRaises(TypeError):
            list(a.zip(1))
