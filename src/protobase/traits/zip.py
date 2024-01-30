# from itertools import pairwise
from typing import Self
from protobase.core import Trait, fields_of


class Zip(Trait):
    def zip(self, *others: tuple[Self]):
        cls = type(self)

        if not all(isinstance(other, cls) for other in others):
            invalid_classes = filter(lambda other: not isinstance(other, cls), others)
            raise TypeError(f"Cannot zip {cls} with {invalid_classes}")

        for field in fields_of(cls):
            yield field, (
                getattr(self, field),
                *(getattr(other, field) for other in others),
            )
