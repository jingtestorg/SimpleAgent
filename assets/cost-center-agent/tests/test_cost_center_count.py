"""Unit test: agent correctly handles cost center count queries."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage


@pytest.mark.asyncio
async def test_cost_center_count_query(mock_mcp_tools, mock_llm):
    """Test that 'How many cost centers are there?' returns a count answer."""
    from agent import SampleAgent

    # Arrange: LLM returns a count-based answer
    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(content="There are 42 cost centers in the system.")
    )
    agent = SampleAgent()

    # Act
    response = await agent.invoke(
        query="How many cost centers are there?",
        context_id="test-count-001",
        tools=mock_mcp_tools,
    )

    # Assert
    assert response.status == "completed"
    assert response.message is not None
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_count_milestone_logging(mock_mcp_tools, mock_llm, caplog):
    """Test that count query triggers M1 and M2 milestone logs."""
    import logging
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(content="There are 42 cost centers.")
    )
    agent = SampleAgent()

    with caplog.at_level(logging.INFO, logger="agent"):
        await agent.invoke(
            query="How many cost centers are there?",
            context_id="test-count-002",
            tools=mock_mcp_tools,
        )

    log_messages = " ".join(caplog.messages)
    assert "M1.achieved" in log_messages
    assert "M2.achieved" in log_messages
    assert "count" in log_messages
