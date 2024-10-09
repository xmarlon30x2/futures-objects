"""class Future"""
from math import ceil, floor, trunc
from operator import index
from threading import Thread
from typing import Any, Callable, Generator

from .utils import unawait
from .constants import RESERVED_ATTRIBUTES, RESERVED_MAGICS
from .enums import States


class Future[T:Any]:
    """Repecent future objects"""

    def __init__(self, target: Callable[[], T], _before: Any | None = None):
        self._target: Callable[[], T] = target
        self._before: "Future" | None = _before
        self._state: States.types = States.pending
        self._thread: Thread = Thread(target=self._resolve)
        self._thread.start()

    def _resolve(self):
        """Resolve the future"""
        if self._before is not None:
            while self._before._state != States.complete:
                continue
        self._output = self._target()
        self._state = States.complete

    async def _getvalue(self) -> T:
        while self._state != States.complete:
            pass
        return self._output

    def _jump(self, key: str, *args, **kwargs):
        def new_target():
            self._check_awaited()
            return getattr(self._output, key)(*args, **kwargs)
        return Future(target=new_target, _before=self)

    def _express(self, express: Callable[[T], Any]):
        def new_target():
            self._check_awaited()
            return express(self._output)
        return Future(target=new_target, _before=self)

    def _check_awaited(self):
        if not hasattr(self, '_output'):
            raise RuntimeError('Imposible getattribute. Not awaited _before')

    # --------------- magic meths witout jumps ---------------------

    def __getattribute__(self, name: str):
        if name in RESERVED_ATTRIBUTES or name in RESERVED_MAGICS:
            return super().__getattribute__(name)

        def new__target():
            self._check_awaited()
            return getattr(self._output, name)
        new__target.__name__ = name
        return Future(target=new__target, _before=self)

    def __getitem__(self, index:Any|slice|int|str) -> 'list[Future[Any]] | Future[Any]':
        if isinstance(index, slice):
            if index.stop is None:
                return self._express(lambda value: value[index])
            if index.start is not None: start = index.start
            else: start = 0
            if index.step is not None: step = index.step
            else: step = 1
            return [
                self._express(lambda value: value[j])
                for j in range(start, index.stop, step)
            ]
        return self._express(lambda value: value[index])

    def __setattr__(self, name: str, value: Any):
        if name in RESERVED_ATTRIBUTES or name in RESERVED_MAGICS:
            super().__setattr__(name, value)
        else:
            def new_target() -> None:
                self._check_awaited()
                return setattr(self._output, name, value)
            Future[None](target=new_target, _before=self)

    def __call__(self,
                 *args, **kwargs):
        def new_target():
            self._check_awaited()
            return self._output(*args, **kwargs)
        return Future(target=new_target, _before=self)

    def __await__(self) -> Generator[Any, Any, T]:
        return self._getvalue().__await__()

    # ---------------- magic meths used jump ---------------------
    # 2. **Representación del objeto**:
    def __repr__(self) -> str:
        return unawait(self._express(lambda value: repr(value)))

    def __str__(self) -> str:
        return unawait(self._express(lambda value: str(value)))

    def __bytes__(self) -> bytes:
        return unawait(self._express(lambda value: bytes(value)))

    def __format__(self, format_spec):  # no tested
        return self._jump('__format__', format_spec)

    # 3. **Comparación**:
    def __lt__(self, other) -> 'Future[bool]':  # menor que
        return self._express(lambda value: value < other)

    def __le__(self, other) -> 'Future[bool]':  # menor o igual que
        return self._express(lambda value: value <= other)

    def __eq__(self, other):  # igual a
        return self._express(lambda value: value == other)

    def __ne__(self, other):  # no igual a
        return self._express(lambda value: value != other)

    def __gt__(self, other) -> 'Future[bool]':  # mayor que
        return self._express(lambda value: value > other)

    def __ge__(self, other) -> 'Future[bool]':  # mayor o igual que
        return self._express(lambda value: value >= other)

    # 4. **Aritmética**:
    def __add__(self, other) -> 'Future[Any]':  # suma  # no tested
        return self._express(lambda value: value + other)

    def __sub__(self, other):  # resta  # no tested
        return self._express(lambda value: value - other)

    def __mul__(self, other):  # multiplicación  # no tested
        return self._express(lambda value: value * other)

    def __truediv__(self, other):  # división  # no tested
        return self._express(lambda value: value / other)

    def __floordiv__(self, other):  # división entera  # no tested
        return self._express(lambda value: value // other)

    def __mod__(self, other):  # módulo  # no tested
        return self._express(lambda value: value % other)

    def __divmod__(self, other):  # divmod  # no tested
        return self._express(lambda value: (value//other, value % other))

    def __pow__(self, other, modulo=None):  # potencia  # no tested
        return self._express(lambda value: value ** other)

    def __lshift__(self, other):  # desplazamiento a la izquierda  # no tested
        return self._express(lambda value: value << other)

    def __rshift__(self, other):  # desplazamiento a la derecha  # no tested
        return self._express(lambda value: value >> other)

    #7. **Conversión de tipo**:
    def __int__(self):
        return unawait(self._express(lambda value: int(value)))

    def __float__(self):
        return unawait(self._express(lambda value: float(value)))

    def __complex__(self):
        return unawait(self._express(lambda value: complex(value)))

    def __bool__(self):
        return unawait(self._express(lambda value: bool(value)))

    def __index__(self):  # no tested
        return unawait(self._express(lambda value: index(value)))

    def __round__(self, n=None):  # no tested
        return unawait(self._express(lambda value: round(value, n)))

    def __trunc__(self):  # no tested
        return unawait(self._express(lambda value: trunc(value)))

    def __floor__(self):  # no tested
        return unawait(self._express(lambda value: floor(value)))

    def __ceil__(self):  # no tested
        return unawait(self._express(lambda value: ceil(value)))
