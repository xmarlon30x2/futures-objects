"""class Future"""
from threading import Thread
from typing import Any, Callable, Generator

from .constants import RESERVED_ATTRIBUTES, RESERVED_MAGICS
from .enums import States

class Future[T]:
    """Repecent future objects"""
    def __init__(self, target:Callable[[], T], _before:Any | None = None):
        self._target:Callable[[], T] = target
        self._before:"Future" | None = _before
        self._state:States.types = States.pending
        self._thread:Thread = Thread(target=self._resolve)
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

    def _jump(self, key:str, *args, **kwargs):
        def new_target():
            if not hasattr(self, '_output'):
                raise RuntimeError('Imposible call. Not awaited _before')
            return getattr(self._output, key)(*args, **kwargs)
        return Future(target=new_target, _before=self)

    def _express(self, express:Callable[[T], Any]):
        def new_target():
            if not hasattr(self, '_output'):
                raise RuntimeError('Imposible call. Not awaited _before')
            return express(self._output)
        return Future(target=new_target, _before=self)

    def _check_awaited(self):
        if not hasattr(self, '_output'):
            raise RuntimeError('Imposible getattribute. Not awaited _before')

    # --------------- magic meths witout jumps ---------------------

    def __getattribute__(self, name:str):
        if name in RESERVED_ATTRIBUTES or name in RESERVED_MAGICS:
            return super().__getattribute__(name)
        def new__target():
            self._check_awaited()
            return getattr(self._output, name)
        new__target.__name__ = name
        return Future(target=new__target, _before=self)

    def __setattr__(self, name:str, value:Any):
        if name in RESERVED_ATTRIBUTES or name in RESERVED_MAGICS:
            super().__setattr__(name, value)
        else:
            def new_target() -> None:
                self._check_awaited()
                return setattr(self._output, name, value)
            Future[None](target=new_target, _before=self)

    def __call__(self, *args, **kwargs):
        def new_target():
            self._check_awaited()
            return self._output(*args, **kwargs)
        return Future(target=new_target, _before=self)

    def __await__(self) -> Generator[Any, Any, T]:
        return self._getvalue().__await__()

    # ---------------- magic meths used jump ---------------------
    #2. **Representación del objeto**:
    def __repr__(self):
        return self._jump('__repr__')

    def __str__(self):
        return self._jump('__str__')

    def __bytes__(self) -> 'Future[bytes]':
        return self._jump('__bytes__')

    def __format__(self, format_spec):
        return self._jump('__format__', format_spec)

    #3. **Comparación**:
    def __lt__(self, other) -> 'Future[bool]': #menor que
        return self._express(lambda value: value < other)

    def __le__(self, other) -> 'Future[bool]':# (menor o igual que
        return self._express(lambda value: value <= other)

    def __eq__(self, other):# (igual a
        return self._express(lambda value: value == other)

    def __ne__(self, other):# (no igual a
        return self._express(lambda value: value != other)

    def __gt__(self, other) -> 'Future[bool]':# (mayor que
        return self._express(lambda value: value > other)

    def __ge__(self, other) -> 'Future[bool]':# (mayor o igual que
        return self._express(lambda value: value >= other)
