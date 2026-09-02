"""Unit test: agent correctly handles top 5 cost centers queries."""
import pytest
from unittest.mock import AsyncMock
from langchain_core.messages import AIMessage

TOP5_RESPONSE = """Here are the top 5 cost centers:

1. CC0010 - Corporate Finance (Controlling Area: A000, Company Code: 1000)
2. CC0020 - Human Resources (Controlling Area: A000, Company Code: 1000)
3. CC0030 - Information Technology (Controlling Area: A000, Company Code: 1000)
4. CC0040 - Sales & Marketing (Controlling Area: A000, Company Code: 1000)
5. CC0050 - Operations (Controlling Area: A000, Company Code: 1000)
"""


@pytest.mark.asyncio
async def test_top_5_cost_centers_query(mock_mcp_tools, mock_llm):
    """Test that 'What are the top 5 cost centers?' returns a list of 5."""
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=TOP5_RESPONSE))
    agent = SampleAgent()

    response = await agent.invoke(
        query="What are the top 5 cost centers?",
        context_id="test-top5-001",
        tools=mock_mcp_tools,
    )

    assert response.status == "completed"
    assert response.message is not None
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_top5_milestone_logging(mock_mcp_tools, mock_llm, caplog):
    """Test that top-5 query triggers M2 with 'top5' intent."""
    import logging
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=TOP5_RESPONSE))
    agent = SampleAgent()

    with caplog.at_level(logging.INFO, logger="agent"):
        await agent.invoke(
            query="What are the top 5 cost centers?",
            context_id="test-top5-002",
            tools=mock_mcp_tools,
        )

    log_messages = " ".join(caplog.messages)
    assert "M1.achieved" in log_messages
    assert "M2.achieved" in log_messages
    assert "top5" in log_messages
