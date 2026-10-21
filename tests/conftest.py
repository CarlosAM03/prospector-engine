"""Installed-package tests; no sys.path injection and no implicit live traffic."""

import os


def pytest_collection_modifyitems(config, items):
    if os.environ.get("PROSPECTOR_RUN_E2E") == "1":
        return
    deselected = [item for item in items if "e2e" in item.keywords]
    items[:] = [item for item in items if "e2e" not in item.keywords]
    if deselected:
        config.hook.pytest_deselected(items=deselected)
