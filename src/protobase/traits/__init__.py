from .weak import Weak
from .dynamic_attrs import DynamicAttrs
from .init import Init
from .repr import Repr
from .hash import Hash
from .cmp import Eq, Cmp
from .inmutable import Inmutable, is_inmutable, know_inmutable
from .consed import Consed, consed_count

Common = (Cmp, Hash, Eq, Repr, Init)


class Basic(Cmp, Hash, Eq, Repr, Init): ...
