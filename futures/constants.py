"""Constants"""
RESERVED_ATTRIBUTES:list[str] = [
    "_target", "_resolve", "_output", "_before", "_state",
    "__await__", "_getvalue",
    "__str__", "_thread",'_jump', '_check_awaited', '_express',
]

RESERVED_MAGICS:list[str] = [
    '__init__',
    '__getattribute__',
    '__setattr__',
    '__call__',
    '__await__',
    '__repr__',
    '__str__',
    '__bytes__',
    '__format__',
    '__lt__',
    '__le__',
    '__eq__',
    '__ne__',
    '__gt__',
    '__ge__',
]