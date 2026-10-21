"""Request -> safe checkpoint -> owned cleanup -> explicit control-flow outcome."""

import pytest

from prospector_engine import (
    CancellationRequested,
    CancellationToken,
    EngineConfig,
    ProspectorEngine,
    SearchQuery,
    Source,
    cancellation_scope,
    observe_execution,
)
from prospector_engine.engines import browser_runtime
from prospector_engine.scraper.google_maps import scraper


def test_cancellation_inside_source_closes_real_runtime_owner(monkeypatch):
    closed = []

    class Page:
        def close(self):
            closed.append("page")

    class Browser:
        version = "controlled"

        def new_page(self):
            return Page()

        def close(self):
            closed.append("browser")

    class Playwright:
        def __enter__(self):
            self.chromium = self
            return self

        def launch(self, **kwargs):
            return Browser()

        def __exit__(self, *args):
            closed.append("driver")

    monkeypatch.setattr(browser_runtime, "sync_playwright", Playwright)
    monkeypatch.setattr(scraper, "create_search_page", lambda *a, **kw: kw["page_factory"]())
    token = CancellationToken()

    def listener(event):
        if event.kind == "stage_completed" and event.stage == "navigation":
            token.request_cancel()

    with (
        cancellation_scope(token),
        observe_execution(listener),
        pytest.raises(CancellationRequested),
    ):
        ProspectorEngine(EngineConfig()).search(SearchQuery(Source.GOOGLE_MAPS, "cafe", "TJ"))
    assert closed == ["page", "browser", "driver"]
    # Binding was restored; future executions do not inherit the cancelled token.
    from prospector_engine.cancellation import checkpoint

    checkpoint()
