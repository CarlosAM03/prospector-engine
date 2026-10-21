"""Cooperative synchronous cancellation at existing execution checkpoints."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Event


class CancellationRequested(BaseException):
    """Explicit control flow; bypass ordinary extraction/observer recovery handlers.

    Catch explicitly in the consumer. Completed browser calls cannot be interrupted.
    Cancellation discards the current search/batch return value; no resume is provided.
    """


class CancellationToken:
    """One-shot token; request_cancel may be called by another thread."""

    def __init__(self) -> None:
        self._requested = Event()

    @property
    def is_cancelled(self) -> bool:
        return self._requested.is_set()

    def request_cancel(self) -> None:
        self._requested.set()

    def raise_if_cancelled(self) -> None:
        if self.is_cancelled:
            raise CancellationRequested("Extraction cancelled at a safe checkpoint")


_token: ContextVar[CancellationToken | None] = ContextVar("prospector_cancellation", default=None)


def checkpoint() -> None:
    token = _token.get()
    if token is not None:
        token.raise_if_cancelled()


@contextmanager
def cancellation_scope(token: CancellationToken) -> Iterator[None]:
    """Bind on the thread running Engine; request the same token from elsewhere."""
    if not isinstance(token, CancellationToken):
        raise TypeError("token must be a CancellationToken")
    binding = _token.set(token)
    try:
        yield
    finally:
        _token.reset(binding)
