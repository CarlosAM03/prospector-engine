"""Consumer contracts added by the independent package."""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

import prospector_engine as api
from prospector_engine.engines import prospector_engine as facade
from prospector_engine.models.source_identity import VerificationState


def query():
    return api.SearchQuery(api.Source.GOOGLE_MAPS, "cafes", "Tijuana")


def source(*args, **kwargs):
    return SimpleNamespace(
        query=args[0],
        businesses=[api.Business(" Cafe "), api.Business("Other")],
        issues=[],
        identities=[
            api.SourceIdentityEvidence(
                api.VerifiedSourceIdentity(api.Source.GOOGLE_MAPS, "google_place_id", "ChIJtest"),
                VerificationState.VERIFIED,
                "controlled_fixture",
            ),
            api.SourceIdentityEvidence.unverified(),
        ],
    )


def test_public_identity_is_aligned_for_single_batch_and_unknown_constructor(monkeypatch):
    monkeypatch.setattr(facade, "_run_google_maps", source)
    engine = api.ProspectorEngine(api.EngineConfig(limit=2))
    result = engine.search(query())
    assert result.source_identities[0].verified.value == "ChIJtest"
    assert result.source_identities[1].verification_state is VerificationState.UNVERIFIED
    assert [b.name for b in result.businesses] == ["CAFE", "OTHER"]
    assert [b.name for b in result.original_businesses] == [" Cafe ", "Other"]
    assert "place_id" not in vars(result.original_businesses[0])
    batch = engine.search_many([api.BatchQuery(query(), 2), api.BatchQuery(query(), 2)])
    assert batch.entries[1].result.source_identities == result.source_identities
    assert batch.entries[1].export_indices == [1]
    constructed = api.SearchResult(
        query(), result.businesses, original_businesses=result.original_businesses
    )
    assert all(x.verified is None for x in constructed.source_identities)
    with pytest.raises(ValueError, match="align"):
        api.SearchResult(
            query(),
            result.businesses,
            original_businesses=result.original_businesses,
            source_identities=(api.SourceIdentityEvidence.unverified(),),
        )


def test_runtime_configuration_reaches_single_and_batch_source(monkeypatch):
    calls = []

    def configured(*args, **kwargs):
        calls.append(kwargs)
        return source(*args, **kwargs)

    monkeypatch.setattr(facade, "_run_google_maps", configured)
    engine = api.ProspectorEngine(api.EngineConfig(limit=2, headless=True, browser_channel=None))
    engine.search(query())
    engine.search_many([api.BatchQuery(query(), 2)])
    assert all(x["browser_channel"] is None and x["headless"] for x in calls)
    assert api.EngineConfig().browser_channel == "msedge"
    with pytest.raises(ValueError, match="browser_channel"):
        api.EngineConfig(browser_channel="unknown")


def test_public_observer_scope_resets_after_failure(monkeypatch):
    monkeypatch.setattr(facade, "_run_google_maps", source)
    events = []
    with api.observe_execution(events.append):
        api.ProspectorEngine(api.EngineConfig(limit=2)).search(query())
    count = len(events)
    api.ProspectorEngine(api.EngineConfig(limit=2)).search(query())
    assert len(events) == count
    assert isinstance(events[0], api.ExecutionEvent)


def test_precancelled_token_prevents_single_and_batch_source(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("cancelled execution reached source")

    monkeypatch.setattr(facade, "_run_google_maps", unexpected)
    engine = api.ProspectorEngine(api.EngineConfig())
    token = api.CancellationToken()
    token.request_cancel()
    for execute in (
        lambda: engine.search(query()),
        lambda: engine.search_many([api.BatchQuery(query(), 1)]),
    ):
        with api.cancellation_scope(token), pytest.raises(api.CancellationRequested):
            execute()
    with api.cancellation_scope(api.CancellationToken()):
        assert token.is_cancelled


def test_package_dependency_direction_covers_actual_files():
    root = Path(api.__file__).parent
    files = list(root.rglob("*.py"))
    assert len(files) >= 53
    forbidden = {
        "rich",
        "fastapi",
        "cli_runtime",
        "cli_app",
        "app_paths",
        "services",
        "exporters",
        "engines",
        "models",
        "scraper",
        "utils",
        "src",
    }
    for file in files:
        for node in ast.walk(ast.parse(file.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] not in forbidden for alias in node.names), file
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                assert (node.module or "").split(".")[0] not in forbidden, file


def test_public_exports_are_explicit():
    assert all(hasattr(api, name) for name in api.__all__)
    assert "_run_google_maps" not in api.__all__
