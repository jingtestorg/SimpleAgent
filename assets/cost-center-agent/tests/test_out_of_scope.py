"""Unit test: agent politely declines out-of-scope queries."""
import pytest
from unittest.mock import AsyncMock
from langchain_core.messages import AIMessage


@pytest.mark.asyncio
async def test_out_of_scope_query_returns_polite_message(mock_mcp_tools, mock_llm):
    """Test that an unrecognized query receives a polite out-of-scope response."""
    from agent import SampleAgent

    out_of_scope_reply = (
        "I'm sorry, but that query is outside my scope. "
        "I can only answer questions about the total count of cost centers "
        "or list the top 5 cost centers."
    )
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=out_of_scope_reply))
    agent = SampleAgent()

    response = await agent.invoke(
        query="What is the weather today?",
        context_id="test-oos-001",
        tools=mock_mcp_tools,
    )

    assert response.status == "completed"
    assert response.message is not None


@pytest.mark.asyncio
async def test_out_of_scope_logs_m2_missed(mock_mcp_tools, mock_llm, caplog):
    """Test that out-of-scope query logs M2.missed."""
    import logging
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(content="That is outside my scope.")
    )
    agent = SampleAgent()

    with caplog.at_level(logging.WARNING, logger="agent"):
        await agent.invoke(
            query="Tell me a joke",
            context_id="test-oos-002",
            tools=mock_mcp_tools,
        )

    log_messages = " ".join(caplog.messages)
    assert "M2.missed" in log_messages
