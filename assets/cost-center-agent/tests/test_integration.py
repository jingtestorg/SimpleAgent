"""Integration test: end-to-end agent flow for cost center queries."""
import pytest
from unittest.mock import AsyncMock
from langchain_core.messages import AIMessage


@pytest.mark.asyncio
async def test_full_count_flow(mock_mcp_tools, mock_llm):
    """End-to-end: natural language count query → invoke → completed answer."""
    from agent import SampleAgent

    expected_answer = "There are 42 cost centers in the SAP S/4HANA system."
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=expected_answer))

    agent = SampleAgent()
    response = await agent.invoke(
        query="How many cost centers are there?",
        context_id="integration-count-001",
        tools=mock_mcp_tools,
    )

    assert response.status == "completed"
    assert response.message is not None
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_full_top5_flow(mock_mcp_tools, mock_llm):
    """End-to-end: top 5 query → invoke → completed answer with list."""
    from agent import SampleAgent

    expected_answer = (
        "Here are the top 5 cost centers:\n"
        "1. CC0010 - Corporate Finance\n"
        "2. CC0020 - Human Resources\n"
        "3. CC0030 - IT\n"
        "4. CC0040 - Sales\n"
        "5. CC0050 - Operations"
    )
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=expected_answer))

    agent = SampleAgent()
    response = await agent.invoke(
        query="What are the top 5 cost centers?",
        context_id="integration-top5-001",
        tools=mock_mcp_tools,
    )

    assert response.status == "completed"
    assert response.message is not None


@pytest.mark.asyncio
async def test_stream_yields_processing_then_result(mock_mcp_tools, mock_llm):
    """Test that stream() first yields a 'Processing...' message, then the final answer."""
    from agent import SampleAgent

    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(content="There are 42 cost centers.")
    )
    agent = SampleAgent()

    chunks = []
    async for chunk in agent.stream(
        query="How many cost centers are there?",
        context_id="integration-stream-001",
        tools=mock_mcp_tools,
    ):
        chunks.append(chunk)

    assert len(chunks) >= 2
    # First chunk should indicate processing
    assert not chunks[0]["is_task_complete"]
    assert "Processing" in chunks[0]["content"]
    # Last chunk should be completed
    assert chunks[-1]["is_task_complete"]
    assert chunks[-1]["content"] is not None
