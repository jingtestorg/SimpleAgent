# Specification: cost-center-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` for full context
- [x] Bootstrap agent code in `assets/cost-center-agent/` using the `sap-agent-bootstrap` skill (invoke from inside `assets/cost-center-agent/`):
  - Agent name: `cost-center-agent`
  - Agent description: `An AI agent for Finance Controllers that answers natural language queries about SAP S/4HANA cost center data, including total cost center count and top 5 cost centers.`
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

No runtime skill is needed — the agent handles exactly two intent types (count, top 5) via system prompt and MCP tool calls; no multi-step workflow or reference material required.

---

## Project-Specific Tasks

### MCP Server Setup (Path A — API Spec → MCP Translation)

- [x] Verify `specification/cost-center-agent/api-specs/CE_COSTCENTER_0001.edmx` exists (already downloaded)
- [x] Verify `specification/cost-center-agent/api-specs/translation.json` exists (already generated — 19 tools)
- [x] Invoke `setup-solution` skill to create the MCP server asset from the translation file at `specification/cost-center-agent/api-specs/`
- [x] Read the generated MCP server `asset.yaml` and copy its `ordId` value exactly — do NOT invent an ORD ID

### Agent System Prompt

- [x] Write a focused system prompt in `app/agent.py` that:
  - Describes the agent as a Finance Controller assistant for SAP S/4HANA cost center queries
  - Instructs the agent to handle exactly two query types:
    1. Total count of cost centers (`$count` or `$top=100` with counting)
    2. Top 5 cost centers (retrieve first 5 using `$top=5`)
  - Includes the mandatory MCP guardrail: "IMPORTANT: You MUST use tools to retrieve live data. Never fabricate, guess, or invent data. Relay tool errors verbatim without adding suggestions."
  - Instructs: "When calling tools that support pagination, always set the page size parameter (top) to a maximum of 100 items."
  - Instructs: "For out-of-scope queries (not cost center count or top 5), respond politely that this query is outside your scope."
  - Is read-only: never invoke create, update, or delete actions

### Agent Tool Wiring

- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module (bootstrap-generated indirection layer)
- [x] Add the MCP server dependency to `asset.yaml` under `requires` using the exact ORD ID from the generated MCP server `asset.yaml`

### Key Query Behaviours

- [x] Agent correctly handles "How many cost centers are there?" → calls list tool with `$top=1&$count=true` or similar, returns count
- [x] Agent correctly handles "What are the top 5 cost centers?" → calls list tool with `$top=5`, returns formatted list with CostCenter, CostCenterName, ControllingArea, CompanyCode
- [x] Agent returns a polite out-of-scope message for unrecognized queries
- [x] Agent returns the exact tool error message if the MCP call fails (no embellishment)

---

## Business Instrumentation

- [x] Implement all 5 milestones from the PRD with structured logging and OpenTelemetry spans:
  - `M1.achieved: user query received` / `M1.missed: no user query received or session timed out`
  - `M2.achieved: intent classified as [count|top5]` / `M2.missed: intent classification failed or query out of scope`
  - `M3.achieved: MCP tool CE_COSTCENTER_0001 called successfully` / `M3.missed: MCP tool call failed or timed out`
  - `M4.achieved: response formatted and ready for delivery` / `M4.missed: response formatting failed due to unexpected MCP result structure`
  - `M5.achieved: answer delivered within SLA` / `M5.missed: answer delivery exceeded 10-second SLA or failed`
- [x] Extract business logic from `stream()` into `_run_agent()` plain async helper; instrument that helper with OpenTelemetry spans (not the generator)
- [x] Verify `auto_instrument()` is called at top of `main.py` before any AI framework imports

---

## MCP Mock & Testing Setup

- [x] After `setup-solution` and MCP server asset creation complete, generate `mcp-mock.json` using the `mcp-mock-config` skill (required before tests can run)
- [x] `conftest.py` only sets `IBD_TESTING=true`

### Unit Tests (`assets/cost-center-agent/tests/`)

- [x] `test_cost_center_count.py` — test the agent's response to "How many cost centers are there?" with mocked MCP returning a list; verify count is extracted and returned correctly
- [x] `test_top_5_cost_centers.py` — test the agent's response to "What are the top 5 cost centers?" with mocked MCP returning 5 records; verify all 5 are presented with name and controlling area
- [x] `test_out_of_scope.py` — test the agent's response to an unrecognized query; verify out-of-scope message is returned without tool call
- [x] `test_mcp_error_handling.py` — test the agent's response when MCP tool returns an error; verify the error message is relayed verbatim

### Integration Test

- [x] `test_integration.py` — end-to-end test: send a natural language query ("How many cost centers?"), mock the LLM responses and MCP tool calls, verify the full flow produces a correct answer

### Final Validation

- [x] Run `pytest` from `assets/cost-center-agent/` (no extra flags) — coverage must be ≥ 70% (actual: 79%)
- [x] Verify `grep -c "^@agent_model\|^@agent_config\|^@prompt_section" assets/cost-center-agent/app/agent.py` returns 9 ✓
- [x] Run `pytest` again (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/cost-center-agent/` ✓
- [x] Verify `grep -r "M[0-9]\.achieved" assets/cost-center-agent/app/` returns results ✓
- [x] Verify `grep -r "sap_cloud_sdk.agent_decorators" assets/cost-center-agent/app/` returns results ✓
