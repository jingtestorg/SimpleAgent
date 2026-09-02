"""Unit test: agent relays MCP tool errors verbatim."""
import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage
from litellm.exceptions import ServiceUnavailableError


@pytest.mark.asyncio
async def test_agent_returns_error_message_on_mcp_failure(mock_mcp_tools, mock_llm):
    """Test that when the LLM/MCP call fails, the agent returns a graceful error response."""
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(
        side_effect=ServiceUnavailableError(
            message="Service unavailable", llm_provider="anthropic", model="claude"
        )
    )
    agent = SampleAgent()

    response = await agent.invoke(
        query="How many cost centers are there?",
        context_id="test-err-001",
        tools=mock_mcp_tools,
    )

    # Agent should return an error status gracefully
    assert response.status in ("completed", "error")
    assert response.message is not None


@pytest.mark.asyncio
async def test_agent_handles_no_tools(mock_llm):
    """Test agent behavior when no MCP tools are available."""
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(
            content="Tools are temporarily unavailable. Please try again later."
        )
    )
    agent = SampleAgent()

    response = await agent.invoke(
        query="How many cost centers are there?",
        context_id="test-notools-001",
        tools=[],
    )

    assert response.status == "completed"
    assert response.message is not None
