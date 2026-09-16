"""Unit tests for the time_tool — one test per time-of-day category."""
import sys
import os
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from tools.time_tool import get_time_of_day, _classify_time_of_day


class TestClassifyTimeOfDay:
    """Unit tests for the _classify_time_of_day helper."""

    def test_morning_start(self):
        assert _classify_time_of_day(0) == "morning"

    def test_morning_middle(self):
        assert _classify_time_of_day(6) == "morning"

    def test_morning_end(self):
        assert _classify_time_of_day(11) == "morning"

    def test_afternoon_start(self):
        assert _classify_time_of_day(12) == "afternoon"

    def test_afternoon_middle(self):
        assert _classify_time_of_day(14) == "afternoon"

    def test_afternoon_end(self):
        assert _classify_time_of_day(16) == "afternoon"

    def test_evening_start(self):
        assert _classify_time_of_day(17) == "evening"

    def test_evening_middle(self):
        assert _classify_time_of_day(19) == "evening"

    def test_evening_end(self):
        assert _classify_time_of_day(20) == "evening"

    def test_night_start(self):
        assert _classify_time_of_day(21) == "night"

    def test_night_middle(self):
        assert _classify_time_of_day(23) == "night"


class TestGetTimeOfDayTool:
    """Tests for the get_time_of_day LangChain tool."""

    def _invoke(self, hour: int) -> dict:
        """Helper: invoke the tool with a mocked clock at the given hour."""
        mock_dt = datetime(2024, 6, 15, hour, 30, 0)
        with patch("tools.time_tool.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_dt
            return get_time_of_day.invoke({})

    def test_morning_greeting(self):
        result = self._invoke(8)
        assert result["category"] == "morning"
        assert result["greeting"] == "Good morning"
        assert result["hour"] == 8

    def test_afternoon_greeting(self):
        result = self._invoke(14)
        assert result["category"] == "afternoon"
        assert result["greeting"] == "Good afternoon"
        assert result["hour"] == 14

    def test_evening_greeting(self):
        result = self._invoke(19)
        assert result["category"] == "evening"
        assert result["greeting"] == "Good evening"
        assert result["hour"] == 19

    def test_night_greeting(self):
        result = self._invoke(22)
        assert result["category"] == "night"
        assert result["greeting"] == "Good night"
        assert result["hour"] == 22

    def test_returns_dict_with_required_keys(self):
        result = self._invoke(10)
        assert "category" in result
        assert "greeting" in result
        assert "hour" in result
