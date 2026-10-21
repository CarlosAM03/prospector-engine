"""Core-only functions from frozen tests/unit/test_utils.py; naming/export excluded."""

from prospector_engine.utils.parser import is_phone


def test_is_phone_accepts_selected_supported_forms():
    assert is_phone("555 123 4567") is True
    assert is_phone("555-123-4567") is True


def test_is_phone_rejects_non_phone_text():
    assert is_phone("abc") is False
    assert is_phone("") is False
