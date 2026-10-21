"""Real browser availability, local HTTP navigation and cleanup."""

import pytest
from prospector_engine.diagnostics import browser_smoke


@pytest.mark.browser
def test_chromium_available_and_owned_resources_close():
    browser_smoke()
