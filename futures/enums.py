from typing import Literal


class States:
    pending: Literal['pending'] = 'pending'
    complete: Literal['complete'] = 'complete'
    types = Literal['complete', 'pending']