"""
    Tests to ensure no one breaks autovivification by mistake.
"""

from analyzer.util import AutovivifiedDict


def test_can_read_undefined_without_error():
    d = AutovivifiedDict()
    assert d['not-defined-yet'] == {}
    assert d['not-defined-yet']['also-not-defined'] == {}
    assert d['not-defined-yet']['also-not-defined']['still-nothing'] == {}
