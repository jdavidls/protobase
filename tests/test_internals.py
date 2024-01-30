# %%
import unittest

from protobase.core import Base
from protobase.traits import Eq, Hash, Repr, Init, Consed


class A(Base, Init):
    a: int = 1


class B(A):
    b: int = 2


class C(B):
    c: int = 3


class MroDescriptorTest(unittest.TestCase):
    def test_descriptor_slots(self):
        self.assertIn("a", B.__dict__)
        self.assertIn("b", C.__dict__)
        self.assertIn("a", C.__dict__)

    def test_mro_dispatch(self):
        C(a=1, b=2, c=3)
        A(a=1)
        B(a=1, b=2)
