"""Integration test — end-to-end agent flow with mocked LLM and external systems."""
import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Set IBD_TESTING before any agent imports
os.environ.setdefault("IBD_TESTING", "true")
os.environ.setdefault("OPENWEATHERMAP_API_KEY", "test-key")


MOCK_WEATHER_API_RESPONSE = {
    "name": "Berlin",
    "weather": [{"description": "partly cloudy"}],
    "main": {
        "temp": 18.0,
        "humidity": 60,
        "feels_like": 17.5,
    },
}


def _make_llm_response(content: str):
    """Build a minimal mock LLM response dict as LangGraph ainvoke returns."""
    from langchain_core.messages import AIMessage
    msg = AIMessage(content=content)
    return {"messages": [msg]}


@pytest.mark.asyncio
class TestAgentIntegration:

    @patch("tools.weather_tool.requests.get")
    @patch("tools.time_tool.datetime")
    async def test_greeting_combines_time_and_weather(self, mock_dt, mock_get):
        """Agent should return a greeting that references both time of day and weather."""
        # Mock clock to 9am (morning)
        mock_dt.now.return_value = datetime(2024, 6, 15, 9, 0, 0)
        # Mock weather API
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = MOCK_WEATHER_API_RESPONSE
        mock_get.return_value = mock_resp

        # Import agent here so IBD_TESTING env var is already set
        from agent import SampleAgent

        agent = SampleAgent()

        # Mock the LLM to return a canned greeting
        expected_content = "Good morning! It's currently 18.0°C and partly cloudy in Berlin."
        mock_result = _make_llm_response(expected_content)

        with patch.object(agent, "_invoke_with_fallback", new=AsyncMock(return_value=mock_result)):
            from tools.time_tool import get_time_of_day
            from tools.weather_tool import get_weather
            response = await agent.invoke("Hello!", "test-context-001", tools=[get_time_of_day, get_weather])

        assert response.status == "completed"
        assert "morning" in response.message.lower() or "18" in response.message

    @patch("tools.weather_tool.requests.get")
    @patch("tools.time_tool.datetime")
    async def test_agent_stream_yields_completed_status(self, mock_dt, mock_get):
        """Agent stream() should yield a final chunk with is_task_complete=True."""
        mock_dt.now.return_value = datetime(2024, 6, 15, 14, 0, 0)
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = MOCK_WEATHER_API_RESPONSE
        mock_get.return_value = mock_resp

        from agent import SampleAgent

        agent = SampleAgent()
        expected_content = "Good afternoon! It's 18.0°C and partly cloudy in Berlin."
        mock_result = _make_llm_response(expected_content)

        with patch.object(agent, "_invoke_with_fallback", new=AsyncMock(return_value=mock_result)):
            from tools.time_tool import get_time_of_day
            from tools.weather_tool import get_weather
            chunks = []
            async for chunk in agent.stream("What's the weather?", "test-context-002", tools=[get_time_of_day, get_weather]):
                chunks.append(chunk)

        assert len(chunks) >= 2
        final_chunk = chunks[-1]
        assert final_chunk["is_task_complete"] is True
        assert expected_content in final_chunk["content"]

    @patch("tools.weather_tool.requests.get")
    @patch("tools.time_tool.datetime")
    async def test_agent_handles_weather_api_failure_gracefully(self, mock_dt, mock_get):
        """When weather API fails, agent should still return a response (time-only fallback)."""
        mock_dt.now.return_value = datetime(2024, 6, 15, 20, 0, 0)
        import requests as req
        mock_get.side_effect = req.exceptions.ConnectionError("Network down")

        from agent import SampleAgent

        agent = SampleAgent()
        fallback_content = "Good evening! Weather data is currently unavailable."
        mock_result = _make_llm_response(fallback_content)

        with patch.object(agent, "_invoke_with_fallback", new=AsyncMock(return_value=mock_result)):
            from tools.time_tool import get_time_of_day
            from tools.weather_tool import get_weather
            response = await agent.invoke("Hello!", "test-context-003", tools=[get_time_of_day, get_weather])

        assert response.status == "completed"
        assert len(response.message) > 0
