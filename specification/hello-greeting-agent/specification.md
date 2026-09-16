# Specification: hello-greeting-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` for full context
- [x] No Data Product ORD IDs recorded in intent.md — skip Data Dependencies section
- [x] Bootstrap agent code in `assets/hello-greeting-agent/` using the `sap-agent-bootstrap` instructions
- [x] Install dependencies; validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> Decision: No runtime skills required — instructions fit cleanly in the system prompt.

---

## Project-Specific Tasks

### REQ-01 — Time-Aware Greeting

- [x] Create `assets/hello-greeting-agent/app/tools/time_tool.py` with `get_time_of_day()` returning morning/afternoon/evening/night
- [x] Expose `get_time_of_day` as a LangChain tool with a clear docstring
- [x] Emit structured logs `[M2.achieved]` / `[M2.missed]`

### REQ-02 — Live Weather Data Retrieval

- [x] Create `assets/hello-greeting-agent/app/tools/weather_tool.py` with `get_weather(location)` calling OpenWeatherMap API
- [x] Falls back to `DEFAULT_LOCATION` env var (defaults to "Berlin") when location is empty
- [x] Raises descriptive exceptions on API failure for graceful agent fallback
- [x] Expose `get_weather` as a LangChain tool with a clear docstring
- [x] Emit structured logs `[M1.achieved]` / `[M1.missed]`

### REQ-03 — Combined Personalised Greeting

- [x] System prompt instructs agent to call both tools and combine into single sentence
- [x] System prompt instructs graceful fallback to time-only greeting when weather fails

### REQ-04 — Conversational Follow-Up on Weather

- [x] System prompt instructs agent to retain weather context and handle follow-up questions

### REQ-05 — Fallback Default Location

- [x] `get_weather` uses `DEFAULT_LOCATION` env var (defaults to "Berlin") when no location provided

---

## Business Instrumentation

- [x] All 5 milestones (M1–M5) emit structured log statements with pattern `[MILESTONE_ID].[achieved|missed]: [description]`
- [x] OpenTelemetry spans wired via bootstrap template
- [x] `bootstrap(app)` called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> No SAP API or MCP server required — both tools are native Python. All MCP tasks skipped.

---

## Testing

- [x] Test dependencies installed
- [x] `tests/test_time_tool.py` — 16 unit tests for all four time categories; all pass
- [x] `tests/test_weather_tool.py` — 8 unit tests for successful fetch, fallback, API failure; all pass
- [x] `tests/test_integration.py` — 3 end-to-end integration tests with mocked LLM; all pass
- [x] Full `pytest` run: 131 passed, 77% coverage (≥70% ✓)
- [x] `app/agent.py` has exactly 5 decorated functions (confirmed: `grep -c` returns 5) ✓
- [x] Final `pytest` run generated `test_report.json` ✓
- [x] `test_report.json` exists in `assets/hello-greeting-agent/` ✓
