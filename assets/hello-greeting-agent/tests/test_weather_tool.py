"""Unit tests for the weather_tool."""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from tools.weather_tool import get_weather


MOCK_API_RESPONSE = {
    "name": "Berlin",
    "weather": [{"description": "partly cloudy"}],
    "main": {
        "temp": 18.4,
        "humidity": 62,
        "feels_like": 17.9,
    },
}


def _mock_response(status_code=200, json_data=None, raise_for_status=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or MOCK_API_RESPONSE
    if raise_for_status:
        mock.raise_for_status.side_effect = raise_for_status
    else:
        mock.raise_for_status.return_value = None
    return mock


class TestGetWeatherTool:
    """Unit tests for the get_weather LangChain tool."""

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"})
    @patch("tools.weather_tool.requests.get")
    def test_successful_fetch_returns_expected_keys(self, mock_get):
        mock_get.return_value = _mock_response()
        result = get_weather.invoke({"location": "Berlin"})
        assert result["location"] == "Berlin"
        assert result["description"] == "partly cloudy"
        assert result["temperature"] == 18.4
        assert result["humidity"] == 62
        assert result["feels_like"] == 17.9

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"}, clear=False)
    @patch("tools.weather_tool.requests.get")
    def test_empty_location_uses_env_default(self, mock_get):
        mock_get.return_value = _mock_response()
        with patch.dict(os.environ, {"DEFAULT_LOCATION": "Paris"}):
            result = get_weather.invoke({"location": ""})
        # Should have called API with Paris as the query param
        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["q"] == "Paris"

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"}, clear=False)
    @patch("tools.weather_tool.requests.get")
    def test_missing_location_falls_back_to_berlin(self, mock_get):
        mock_get.return_value = _mock_response()
        # Remove DEFAULT_LOCATION from env if present
        env = {k: v for k, v in os.environ.items() if k != "DEFAULT_LOCATION"}
        env["OPENWEATHERMAP_API_KEY"] = "test-key"
        with patch.dict(os.environ, env, clear=True):
            get_weather.invoke({"location": ""})
        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["q"] == "Berlin"

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_raises_value_error(self):
        with pytest.raises(ValueError, match="OPENWEATHERMAP_API_KEY"):
            get_weather.invoke({"location": "Berlin"})

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"})
    @patch("tools.weather_tool.requests.get")
    def test_http_error_raises_runtime_error(self, mock_get):
        import requests as req
        mock_get.return_value = _mock_response(
            status_code=404,
            raise_for_status=req.exceptions.HTTPError("404 Not Found"),
        )
        with pytest.raises(RuntimeError, match="Weather API returned an error"):
            get_weather.invoke({"location": "InvalidCity"})

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"})
    @patch("tools.weather_tool.requests.get")
    def test_network_error_raises_runtime_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError("Network unreachable")
        with pytest.raises(RuntimeError, match="Weather API network error"):
            get_weather.invoke({"location": "Berlin"})

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"})
    @patch("tools.weather_tool.requests.get")
    def test_temperature_rounded_to_one_decimal(self, mock_get):
        data = {**MOCK_API_RESPONSE, "main": {**MOCK_API_RESPONSE["main"], "temp": 18.456}}
        mock_get.return_value = _mock_response(json_data=data)
        result = get_weather.invoke({"location": "Berlin"})
        assert result["temperature"] == 18.5

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test-key"})
    @patch("tools.weather_tool.requests.get")
    def test_uses_api_key_from_environment(self, mock_get):
        mock_get.return_value = _mock_response()
        get_weather.invoke({"location": "London"})
        call_kwargs = mock_get.call_args
        assert call_kwargs[1]["params"]["appid"] == "test-key"
