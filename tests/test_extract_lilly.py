import pytest
from datetime import date
from extract.daily_info import build_time_window

def test_build_time_window_returns_correct_start_and_end():
    start, end = build_time_window(date(2026, 1, 1))
    
    # start should be midnight UTC on Jan 1, 2026
    assert start == 1767225600
    # end should be 23:59 UTC on the same day
    assert end == 1767311940
