# Hello Agent — Time & Weather Greeting

An AI agent that greets users with a personalised message based on the current time of day and live weather conditions.

## Business challenge

Build a Python AI agent that greets users with a personalised message based on the current time of day and live weather conditions at a configurable location, and can handle follow-up weather questions conversationally.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Agent greeting accuracy in test cases | — | 100% correct greetings | — | Customer Experience / AI Agent demo | user |

## Key Milestones

1. **M1 — Weather retrieval**: Agent successfully retrieves live weather data from OpenWeatherMap API
2. **M2 — Time-aware greeting**: Agent generates correct time-of-day greeting (morning / afternoon / evening / night)
3. **M3 — Weather-aware greeting**: Agent combines time and weather into a personalised greeting
4. **M4 — Conversational follow-up**: Agent handles follow-up weather questions in context
5. **M5 — Demo validation**: All test cases pass; 100% greeting accuracy confirmed

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash (E2E)

### Process Hierarchy

```
Lead to Cash (E2E)
└── Manage Customers and Channels (generic)
    └── Manage customers (generic) [BPS-370]
        └── Manage customer experience
```

### Summary

The greeting agent maps to the "Lead to Cash" E2E under "Manage Customers and Channels", specifically the "Manage customer experience" activity, covering real-time, context-aware customer interactions and personalised engagement.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Data Product ORD ID | Gap? | Notes / assumptions |
|---|---|---|---|---|---|---|---|
| Time-aware greeting | None | — | — | — | — | Yes | System clock used; no SAP product needed |
| Live weather data retrieval | None (Climate Zone Service found but no ORD ID) | — | — | — | — | Yes | External OpenWeatherMap REST API; custom tool required |
| Personalised combined greeting | None | — | — | — | — | Yes | Custom agent logic; A2A Python agent required |
| Conversational follow-up on weather | None | — | — | — | — | Yes | LLM reasoning + custom tool; no standard SAP asset |

### Key findings

- No standard SAP product covers real-time weather-based greeting generation — full custom development required.
- A Python AI agent (A2A protocol) is the appropriate solution category for autonomous, context-aware reasoning.
- Weather data will be sourced from OpenWeatherMap REST API via a custom tool; system clock provides time context.
- SAP Customer Data Platform and SAP Commerce Cloud cover customer management but are out of scope for this PoC.
- No MCP servers exist for weather or time APIs; both will be implemented as native Python agent tools.
- A hardcoded fallback location ensures demo resilience when no location is provided.

## Recommendations

### Python AI Agent — Time & Weather Greeting

#### Executive Summary

Standalone Python A2A agent delivering context-aware greetings using time + weather.

#### Recommended Solution

A pro-code Python agent following the A2A protocol, using the system clock for time-of-day context and OpenWeatherMap REST API for live weather data. The agent generates personalised greetings and handles conversational follow-up questions about weather conditions. Deployed as a standalone PoC on SAP BTP.

#### Recommended solution category

AI Agent

#### Intent fit
95%
