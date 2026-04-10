import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def timed() -> Iterator[callable]:
    start = time.perf_counter()
    def ms() -> int:
        return int((time.perf_counter() - start) * 1000)
    yield ms