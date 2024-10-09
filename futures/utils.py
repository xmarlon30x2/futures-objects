from asyncio import run
from typing import Awaitable, Callable

def unawait[T](promise:Awaitable[T]) -> T:
    async def dispach() -> T:
        return await promise
    return run(dispach())

def unasync[T](func: Callable[..., T]) -> Callable[..., T]:
    def dispach(*args, **kwargs):
        return run(func(*args, **kwargs))
    dispach.__name__ = 'dispach_'+func.__name__
    dispach.__doc__ = func.__doc__
    return dispach
