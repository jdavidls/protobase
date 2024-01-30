from .weak import *
from .dynamic_attrs import *
from .init import *
from .repr import *
from .hash import *
from .cmp import *
from .inmutable import *
from .consed import *

from .zip import *


class Builtin(Cmp, Eq, Hash, Repr, Init):
    """Trait that implements all builtin traits.

    This trait is a composition of the following traits:
        - Cmp
        - Eq
        - Hash
        - Repr
        - Init

    """
