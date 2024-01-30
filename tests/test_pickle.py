# %%
from __future__ import annotations
import unittest
import pickle

from protobase import Base, traits
from protobase.traits.consed import consed_count


def clone[T](obj: T) -> T:
    return pickle.loads(pickle.dumps(obj))


class PickleTest(unittest.TestCase):
    class Root(Base, traits.Cmp, traits.Repr, traits.Init):
        alphas: list[PickleTest.Alpha]
        betas: list[PickleTest.Beta]

        @classmethod
        def new(cls):
            alphas = [PickleTest.Alpha.new(n) for n in range(10)]
            betas = [PickleTest.Beta(n=n, alpha=alphas[n % 10]) for n in range(100)]
            return cls(
                alphas=alphas,
                betas=betas,
            )

    class Alpha(Base, traits.Cmp, traits.Repr, traits.Consed):
        a: int
        b: int

        @classmethod
        def new(cls, n: int):
            return cls(
                a=n,
                b=10 - n,
            )

    class Beta(Base, traits.Cmp, traits.Repr, traits.Init):
        n: int
        alpha: PickleTest.Alpha

    def test_pickling(self):
        root = self.Root.new()
        cloned = clone(root)

        self.assertEqual(root, cloned)
        self.assertEqual(consed_count(self.Alpha), 10)

        for n, beta in enumerate(cloned.betas):
            self.assertEqual(beta, root.betas[n])
            self.assertIs(beta.alpha, root.alphas[n % 10])


# %%
if __name__ == "__main__":
    unittest.main()
