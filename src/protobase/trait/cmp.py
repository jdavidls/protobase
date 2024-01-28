from typing import Literal, Self, Sequence
from protobase.core import Trait, fields_of, impl, protomethod
from protobase.utils import compile_function


class Cmp(Trait):
    @protomethod()
    def __lt__(self, other: Self):
        ...

    @protomethod()
    def __le__(self, other: Self):
        ...

    @protomethod()
    def __gt__(self, other: Self):
        ...

    @protomethod()
    def __ge__(self, other: Self):
        ...


def _compile_cmp_function(
    fn_name: Literal["__lt__", "__le__", "__gt__", "__ge__"],
    fields: Sequence[str],
):
    return compile_function(
        fn_name,
        f"def {fn_name}(self, other):",
        "    if self is other: return True" if fn_name in ("__le__", "__ge__") else "",
        "    if type(self) != type(other): return NotImplemented",
        *[
            f"    if self.{field}.{fn_name}(other.{field}): return True"
            for field in fields
        ],
        "    return False",
    )


@impl(Cmp.__lt__)
def _impl_lt(cls: type[Cmp]):
    return _compile_cmp_function("__lt__", fields_of(cls).keys())


@impl(Cmp.__le__)
def _impl_le(cls: type[Cmp]):
    return _compile_cmp_function("__le__", fields_of(cls).keys())


@impl(Cmp.__gt__)
def _impl_lt(cls: type[Cmp]):
    return _compile_cmp_function("__gt__", fields_of(cls).keys())


@impl(Cmp.__ge__)
def _impl_le(cls: type[Cmp]):
    return _compile_cmp_function("__ge__", fields_of(cls).keys())
