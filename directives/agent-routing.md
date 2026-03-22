# Agent Routing + Mission Control Status Updates

When a message arrives from a Discord channel, route it to the correct team and update Mission Control status.

## Channel → Agent Mapping

| Discord Channel | Agent Name | MC Agent ID |
|---|---|---|
| #requests | Assistant Bot | 14 |
| #briefings | Daily Brief Bot | 6 |
| #daily-brief | Daily Brief Bot | 6 |
| #breaking-news | Breaking News Bot | 12 |
| #seo-tasks | SEO & Email Bot | 3 |
| #email-campaigns | SEO & Email Bot | 3 |
| #growth-results | SEO & Email Bot | 3 |
| #tasks (DEV) | Architect | 9 |
| #builds | Backend Dev | 11 |
| #architecture | Architect | 9 |
| #market-research | Strategy Researcher | 13 |
| #backtests | Backtester | 2 |
| #paper-trading | Paper Trader | 10 |
| #risk-analysis | Risk Analyst | 5 |
| #longform | Longform Bot | 4 |
| #shortform | Shortform Bot | 8 |
| #content-calendar | Longform Bot | 4 |
| #diagrams | Diagrams Bot | 15 |

## Mission Control Status Protocol

**Every time you handle a routed task:**

### 1. Mark agent BUSY (before starting work)
```bash
curl -s -X PUT http://localhost:3000/api/agents \
  -H "x-api-key: 4377667558daf5f6568dc6c5f917e260aa6ca337d93330d6dadcecbcad53ff06" \
  -H "Content-Type: application/json" \
  -d '{"name":"<AGENT_NAME>","status":"busy","last_activity":"<short description of task>"}'
```

### 2. Mark agent IDLE (after task completes)
```bash
curl -s -X PUT http://localhost:3000/api/agents \
  -H "x-api-key: 4377667558daf5f6568dc6c5f917e260aa6ca337d93330d6dadcecbcad53ff06" \
  -H "Content-Type: application/json" \
  -d '{"name":"<AGENT_NAME>","status":"idle","last_activity":"<what was completed>"}'
```

## Routing Rules

- If message comes from a mapped channel → route to that agent, update MC status
- If message is ambiguous (e.g. general chat) → handle as main session, no MC update needed
- For multi-agent tasks (Dev Team, Quant Team) → mark all involved agents busy, idle them as each finishes
- Always update MC — even if the task is simple. This is what makes the dashboard useful.
