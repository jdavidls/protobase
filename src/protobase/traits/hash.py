from protobase.core import Obj, Trait, fields_of, impl, protomethod
from protobase.utils import attr_lookup, compile_function, slots_of


class Hash(Trait):
    """Trait that implements the __hash__ function in a class.

    This implementation of __hash__ hashes all the field values of the object.

    Is the class has the slot __hash_cache__, the hash is cached in that slot.
    This is done to avoid recalculating the hash of the object every time it is
    hashed.

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
    def __hash__(self): ...


@impl(Hash.__hash__)
def _hash_impl(cls: type[Obj]):
    fields = fields_of(cls)

    if "__hash_cache__" in slots_of(cls):
        return compile_function(
            "__hash__",
            f"def __hash__(self):",
            f'    if hasattr(self, "__hash_cache__"):',
            f"        return self.__hash_cache__",
            f'    hash_cache_setter(self, hash(({" ".join(f"self.{field}," for field in fields)})))',
            f"    return self.__hash_cache__",
            globals={"hash_cache_setter": attr_lookup(cls, "__hash_cache__").__set__},
        )
    else:
        return compile_function(
            "__hash__",
            f"def __hash__(self):",
            f'    return hash(({" ".join(f"self.{field}," for field in fields)}))',
        )
