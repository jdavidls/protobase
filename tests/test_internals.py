import unittest

from protobase import Base


class MroDescriptorTest(unittest.TestCase):
    class A(Base):
        a: int = 1

    class B(A):
        b: int = 2

    class C(B):
        c: int = 3

    def test_descriptor_slots(self):
        self.assertIn("a", self.B.__dict__)
        self.assertIn("b", self.C.__dict__)
        self.assertIn("a", self.C.__dict__)

    def test_mro_dispatch(self):
        self.C(a=1, b=2, c=3)
        self.A(a=1)
        self.B(a=1, b=2)
