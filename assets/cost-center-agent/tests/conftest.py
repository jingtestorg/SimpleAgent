"""Test fixtures for cost-center-agent unit and integration tests."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure app/ is on sys.path for peer-level imports
_APP_DIR = str(Path(__file__).parent.parent / "app")
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)


@pytest.fixture
def mock_mcp_tools():
    """Return a minimal list of mock LangChain tools representing the MCP server."""
    from langchain_core.tools import StructuredTool

    def _list_cost_centers(filter: str = "", top: int = 5, **kwargs):
        return {
            "@odata.count": 42,
            "value": [
                {
                    "ControllingArea": "A000",
                    "CostCenter": "CC0010",
                    "CostCenterName": "Corporate Finance",
                    "CompanyCode": "1000",
                },
                {
                    "ControllingArea": "A000",
                    "CostCenter": "CC0020",
                    "CostCenterName": "Human Resources",
                    "CompanyCode": "1000",
                },
                {
                    "ControllingArea": "A000",
                    "CostCenter": "CC0030",
                    "CostCenterName": "Information Technology",
                    "CompanyCode": "1000",
                },
                {
                    "ControllingArea": "A000",
                    "CostCenter": "CC0040",
                    "CostCenterName": "Sales & Marketing",
                    "CompanyCode": "1000",
                },
                {
                    "ControllingArea": "A000",
                    "CostCenter": "CC0050",
                    "CostCenterName": "Operations",
                    "CompanyCode": "1000",
                },
            ],
        }

    def _count_cost_centers(filter: str = "", **kwargs):
        return 42

    list_tool = StructuredTool.from_function(
        func=_list_cost_centers,
        name="list_a_costcenter_2_for_sap_self",
        description="Retrieve a list of cost center entities from A_CostCenter_2.",
    )
    count_tool = StructuredTool.from_function(
        func=_count_cost_centers,
        name="count_a_costcenter_2_for_sap_self",
        description="Get the total count of cost centers.",
    )
    return [list_tool, count_tool]


@pytest.fixture
def mock_llm(add_agent_to_path):
    """Patch ChatLiteLLM so no real AI Core calls are made during tests."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from langchain_core.messages import AIMessage

    mock = MagicMock()
    mock.ainvoke = AsyncMock(
        return_value=AIMessage(content="Mocked LLM response for testing.")
    )
    mock.astream = AsyncMock(return_value=iter([]))
    mock.bind_tools = MagicMock(return_value=mock)

    with patch("agent.ChatLiteLLM", return_value=mock):
        yield mock
