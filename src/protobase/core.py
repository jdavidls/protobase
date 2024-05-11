# %%
from __future__ import annotations

from functools import cached_property
from itertools import chain
from threading import RLock
from types import (
    GetSetDescriptorType,
    MappingProxyType,
    MemberDescriptorType,
    MethodType,
)
from typing import (
    Any,
    Callable,
    Generic,
    NamedTuple,
    Optional,
    ParamSpec,
    TypeVar,
    dataclass_transform,
    get_type_hints,
)


from protobase.utils import mro_of_bases


@dataclass_transform()
class ObjectMeta(type):
    """
    Metaclass for protobase classes.

    This metaclass is responsible for:
    - Generating the __slots__ attribute of the class.
    - Generating the __kwdefaults__ attribute of the class.

    NOTE: The default object instantiation protocol is overriden in
    protobase classes. The __new__ function is responsible for
    calling the __init__ function. This behaviour is choosen
    to allow Consign objects to be pickleable.
    """

    # __kwargs__: dict[str, Any] ## implementamos como un ChainMap según el mro?

    __kwdefaults__: dict[str, Any]
    __attr_cache__: MappingProxyType(dict[str, Any])

    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs
    ):
        bases = mro_of_bases(bases)

        kwdefaults = {}
        base_slots = set()

        for base in reversed(bases):
            if base is object or base is Generic:
                continue
            if not isinstance(base, ObjectMeta):
                raise TypeError(
                    f"Invalid base class: '{base.__qualname__}'."
                    f" All base classes must be 'proto.Base' classes."
                )

            base_slots.update(base.__slots__)
            kwdefaults.update(base.__kwdefaults__)

        fields = namespace.get("__annotations__", {}).keys()

        # TODO: filter annotations values starts by ClassVar[ or Annotation[ClassVar[

        for field in chain(fields, base_slots):
            if field in namespace:
                kwdefaults[field] = namespace.pop(field)

        # if "__slots__" in namespace:
        #     raise TypeError("You cannot define '__slots__' in a ProtoBase class.")
        user_defined_slots = namespace.get("__slots__", ())
        field_slots = tuple(field for field in fields if field not in base_slots)

        for nm, attr in namespace.items():
            if isinstance(attr, cached_property):
                from protobase.attr import slot_cached

                namespace[nm] = slot_cached(attr.func)

        # cached_property_slots = tuple(
        #     attr.__set_name__(None, nm)
        #     for nm, attr in namespace.items()
        #     if isinstance(attr, cached_slot)
        # )

        namespace["__kwdefaults__"] = kwdefaults
        namespace["__slots__"] = (
            *user_defined_slots,
            *field_slots,
            # *cached_property_slots,
        )

        return type.__new__(mcs, name, tuple(bases), namespace)

    def __call__(cls, *args, **kwargs):
        return cls.__class_call__(*args, **kwargs)

    def __class_call__(cls, *args, **kwargs):
        self = cls.__new__(cls, *args, **kwargs)
        self.__init__(*args, **kwargs)
        return self


@dataclass_transform()
class Trait(metaclass=ObjectMeta):  # TODO: Quitar trait de la metaclase
    """
    Base class for all traits.
    Traits are classes whose instances are meant to be used as
    mixins for other classes.
    """

    @classmethod
    def __check_type_hints__(cls):
        pass

    def __new__(cls, *args, **kwargs):
        if is_trait(cls):
            raise TypeError(
                f"Cannot instantiate a bare trait class '{cls.__qualname__}'"
            )

        return object.__new__(cls)


@dataclass_transform()
class Object(Trait, metaclass=ObjectMeta):
    """
    Base class for all protobase classes.
    """

    # def __init_subclass__(cls) -> None:
    #     super().__init_subclass__()

    #     # Pop front on the mro  the class descriptors for slots, protomethods
    #     for base in cls.__mro__:
    #         if not issubclass(base, Trait):
    #             continue

    #         # for nm in base.__slots__:
    #         #     if not nm in cls.__dict__:
    #         #         setattr(cls, nm, base.__dict__[nm])

    #         for nm, item in base.__dict__.items():
    #             if not isinstance(
    #                 item, (trait_method, MemberDescriptorType, GetSetDescriptorType)
    #             ):
    #                 continue

    #             if nm in cls.__dict__:
    #                 continue

    #             # cls.__dict__[nm] = item
    #             setattr(cls, nm, item)


#
def is_trait(cls: type[Object]) -> bool:
    return issubclass(cls, Trait) and not issubclass(cls, Object)


class AttrInfo(NamedTuple):
    name: str
    type: type
    default: Any
    annotations: dict[str, Any]


def fields_of(cls: type[Object]) -> MappingProxyType[str, Any]:
    """
    Get the fields of a protobase class or object.

    """
    assert issubclass(cls, Object)

    if "__attr_cache__" not in cls.__dict__:
        hints = get_type_hints(cls)
        cls.__attr_cache__ = hints
        cls.__check_type_hints__()

    return MappingProxyType(
        {
            nm: tp
            for nm, tp in cls.__dict__["__attr_cache__"].items()
            # if not nm.startswith("_")
        }
    )


Args = ParamSpec("Args")
RType = TypeVar("RType")


class proto_method: ...


class trait_method(Generic[Args, RType]):
    """

    Example:
    >>> class MyTrait(proto.Trait):
    ...     @trait_method
    ...     def my_meth(self, x: int) -> str:
    ...         ...
    >>> @MyTrait.my_meth.implementer()
    ... async def _my_meth_impl(cls: type[MyTrait]):
    ...     fields = attrs(cls).keys()
    ...     return compile_function(
    ...         'my_meth',
    ...         'def my_meth(self): return  "HelloWorld"'
    ...     )

    Args:
        proto_fn (Callable[Args, RType], optional): The prototype
        function to be associated with the method.

    Methods:
        impl(self) -> Callable[[Callable[[type[Base]]], Callable[Args, RType]]]:
        Decorator for setting the implementation function.

    """

    _trait_fn: Callable
    _implementer: Callable
    _implementations: dict[type[Object], Callable]

    def __init__(self, trait_fn: Callable[Args, RType] = None) -> None:
        self._trait_fn = trait_fn
        self._implementer = None
        self._implementations = {}

    def __repr__(self):
        return f"<trait_method {self._trait_fn.__name__}>"

    def implementer(
        self, implementer_fn: Callable[[type[Object]], Callable[Args, RType]]
    ) -> Callable:
        assert self._implementer is None, "Cannot reassign the implementation function."
        self._implementer = implementer_fn
        return implementer_fn

    def __set_name__(self, owner, name):
        if not is_trait(owner):
            raise TypeError(
                f"Cannot define a protobase method '{name}' in a non-trait only class '{owner.__qualname__}'"
            )
        if name != self._trait_fn.__name__:
            raise NameError(
                f"Cannot define a protomethod '{name}' with a different name than '{self._trait_fn.__name__}'"
            )
        # self._owner = owner

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        fn = self._implementations.get(objtype, None)

        if fn is None:
            assert not is_trait(objtype)

            if self._implementer is None:
                raise TypeError(
                    f"Cannot find an implementation function for '{self._trait_fn.__name__}'"
                )

            fn = self._implementer(objtype)
            fn.__name__ = self._trait_fn.__name__
            fn.__module__ = self._trait_fn.__module__
            fn.__doc__ = self._trait_fn.__doc__

            self._implementations[objtype] = fn

        return MethodType(fn, obj)


@dataclass_transform()
def protobase():
    def protobase_decorator(cls):
        return cls

    return protobase_decorator
