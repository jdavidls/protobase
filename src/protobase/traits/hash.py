from protobase import attr
from protobase.core import Object, Trait, fields_of, trait_method
from protobase.traits.cmp import Eq
from protobase.utils import compile_function, slots_of


class Hash(Trait, Eq):
    """Trait that implements the __hash__ function in a class.

    This implementation of __hash__ hashes all the field values of the object.

    Is the class has the slot __hash_cache__, the hash is cached in that slot.
    This is done to avoid recalculating the hash of the object every time it is
    hashed.

    Example:
        >>> class Foo(Object, Hash):
        ...     a: int
        ...     b: int
        ...     c: int
        >>> foo = Foo(1, 2, 3)
        >>> hash(foo)
        3713081631934410656
    """

    @trait_method
    def __hash__(self): ...


@Hash.__hash__.implementer
def _hash_impl(cls: type[Object]):
    # fields = fields_of(cls)

    self_fields = (f"self.{field}," for field in fields_of(cls))
    hash_of_self_fields = f'hash(({" ".join(self_fields)}))'

    if "__hash_cache__" in slots_of(cls):
        return compile_function(
            "def __hash__(self):",
            '    if hasattr(self, "__hash_cache__"):',
            "        return self.__hash_cache__",
            f"    hash_cache_setter(self, {hash_of_self_fields})",
            "    return self.__hash_cache__",
            globals={
                "hash_cache_setter": attr.setter(cls, "__hash_cache__"),
            },
        )
    else:
        return compile_function(
            "def __hash__(self):",
            f"    return {hash_of_self_fields}",
        )


def cached_hash_of(obj: Hash) -> int:
    if hasattr(obj, "__hash_cache__"):
        return obj.__hash_cache__
