"""Public synchronous observer contract, sharing the frozen event implementation."""

from typing import Protocol

from .engines._observability import ExecutionEvent, observe_execution


class EngineObserver(Protocol):
    """Ordinary observer exceptions are logged and ignored by the Engine."""

    def __call__(self, event: ExecutionEvent) -> None: ...


__all__ = ["ExecutionEvent", "EngineObserver", "observe_execution"]
