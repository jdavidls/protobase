# %%
from __future__ import annotations

from itertools import chain
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
    dataclass_transform,
    get_type_hints,
)

from protobase.utils import mro_of_bases


@dataclass_transform()
class Meta(type):
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
            if not isinstance(base, Meta):
                raise TypeError(
                    f"Invalid base class: '{base.__qualname__}'."
                    f" All base classes must be 'proto.Base' classes."
                )

            base_slots.update(base.__slots__)
            kwdefaults.update(base.__kwdefaults__)

        fields = namespace.get("__annotations__", {}).keys()

        for field in chain(fields, base_slots):
            if field in namespace:
                kwdefaults[field] = namespace.pop(field)

        # if "__slots__" in namespace:
        #     raise TypeError("You cannot define '__slots__' in a ProtoBase class.")
        slots = namespace.get("__slots__", ())
        slots = slots + tuple(field for field in fields if field not in base_slots)

        namespace["__slots__"] = tuple(slots)
        namespace["__kwdefaults__"] = kwdefaults

        return type.__new__(mcs, name, tuple(bases), namespace)

    def __call__(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)


@dataclass_transform()
class Trait(metaclass=Meta):
    """
    Base class for all traits.
    Traits are classes whose instances are meant to be used as
    mixins for other classes.
    """

    def __new__(cls, *args, **kwargs):
        if not issubclass(cls, Base):
            raise TypeError(f"Cannot instantiate trait '{cls.__qualname__}'")

        obj = object.__new__(cls)
        obj.__init__(*args, **kwargs)
        return obj

    def __getnewargs_ex__(self):
        return (), {nm: getattr(self, nm) for nm in fields_of(self)}

    def __getstate__(self):
        pass

    def __setstate__(self, state):
        pass


@dataclass_transform()
class Base(Trait, metaclass=Meta):
    """
    Base class for all protobase classes.
    """

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        # Copy proto method descriptors from base traits
        for base in cls.__bases__:
            if base is object:
                # if issubclass(base, Base) or base is object:
                continue

            for nm, item in base.__dict__.items():
                if nm in cls.__dict__:
                    continue

                if isinstance(
                    item, (protomethod, MemberDescriptorType, GetSetDescriptorType)
                ):
                    # cls.__dict__[nm] = item
                    setattr(cls, nm, item)


def fields_of(cls_or_obj: Meta | Base) -> MappingProxyType[str, Any]:
    """
    Get the fields of a protobase class or object.
    """
    if not hasattr(cls_or_obj, "__attr_cache__"):
        cls_or_obj.__attr_cache__ = get_type_hints(cls_or_obj)

    return MappingProxyType(
        {
            nm: tp
            for nm, tp in cls_or_obj.__attr_cache__.items()
            if not nm.startswith("_")
        }
    )


class protomethod[**Args, RType]:
    """

    Example:
    >>> class MyTrait(proto.Trait):
    ...     @proto.method
    ...     def my_meth(self, x: int) -> str:
    ...         ...
    >>> @MyTrait.my_meth.impl()
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

    __slots__ = (
        "_proto_fn",
        "_impl_fn",
        "_owner",
    )
    _proto_fn: Callable
    _impl_fn: Callable
    _owner: type[Base]

    def __init__(self, proto_fn: Callable[Args, RType] = None) -> None:
        if proto_fn is not None:
            self(proto_fn)

    def __call__(self, proto_fn: Callable[Args, RType]):
        self._proto_fn = proto_fn
        return self

    def __set_name__(self, owner, name):
        if self._proto_fn.__name__ != name:
            raise NameError(
                f"Cannot define a protobase method '{name}' with a different name than '{self._proto_fn.__name__}'"
            )
        if not issubclass(owner, Trait) or issubclass(owner, Base):
            raise TypeError(
                f"Cannot define a protobase method '{name}' in a non-trait only class '{owner.__qualname__}'"
            )
        self._owner = owner

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        assert issubclass(objtype, Base)

        fn = self._impl_fn(objtype)
        fn.__name__ = self._proto_fn.__name__
        fn.__module__ = self._proto_fn.__module__
        fn.__doc__ = self._proto_fn.__doc__

        setattr(objtype, self._proto_fn.__name__, fn)  # se sobreescribe el descriptor

        return MethodType(fn, obj)


def impl(target: protomethod):
    """
    Decorator for setting the implementation function of a protobase method.
    """

    def impl_decorator(impl_fn):
        target._impl_fn = impl_fn
        return impl_fn

    return impl_decorator
