from protobase.core import Base, Trait, fields_of, impl, protomethod
from protobase.utils import compile_function


class Hash(Trait):
    """
    Trait that implements the __hash__ function in a class.
    This implementation of __hash__ hashes all the field values of the object.
    Example:
        >>> class Foo(Base, Hash):
        ...     a: int
        ...     b: int
        ...     c: int
        >>> foo = Foo(1, 2, 3)
        >>> hash(foo)
        3713081631934410656
    """

    @protomethod()
    def __hash__(self):
        ...


@impl(Hash.__hash__)
def _hash_impl(cls: type[Base]):
    fields = fields_of(cls).keys()

    return compile_function(
        "__hash__",
        f"def __hash__(self):",
        f'    return hash(({" ".join(f"self.{field}," for field in fields)}))',
    )
