# Model Routing Guide

**Last updated:** 2026-06-04

## How Routing Works

OpenCode routes requests through an Anthropic-compatible proxy on `localhost:3000` (One-API / 9router). The proxy maps model names to actual backend providers.

```
opencode.jsonc
  "model": "9router/cx/gpt-5.3-codex"
        │
        ▼
  proxy (localhost:3000)
        │
        ▼
  actual provider (Anthropic / OpenAI / etc.)
```

## Configured Models

| Model name in config | Proxy route | Use case | Cost tier |
|---|---|---|---|
| `9router/cx/gpt-5.3-codex` | via port 3000 | Complex, multi-file, security | High |
| `9router/gh/gpt-4o-mini` | via port 3000 | Simple tasks, Q&A, boilerplate | Low |
| `ollama-local/llava` | localhost:11434 | Local vision tasks | Free |
| `ollama-local/gemma4` | localhost:11434 | Local text, offline | Free |

## Agent-to-Model Mapping

| Agent | Model | Reason |
|---|---|---|
| `cheap-coder` | `9router/gh/gpt-4o-mini` | High volume, simple tasks |
| `senior-coder` | `9router/cx/gpt-5.3-codex` | Complex, needs reasoning |
| `architect` | `9router/cx/gpt-5.3-codex` | Design decisions |
| `security-auditor` | `9router/cx/gpt-5.3-codex` | Security requires careful reasoning |
| `reviewer` | `9router/cx/gpt-5.3-codex` | Review needs full context |
| `researcher` | `9router/cx/gpt-5.3-codex` | Web search + synthesis |
| `db-analyst` | `9router/cx/gpt-5.3-codex` | Schema analysis |
| `devops` | `9router/cx/gpt-5.3-codex` | Infrastructure changes |
| `automation-planner` | `9router/gh/gpt-4o-mini` | Planning, low stakes |
| `cost-optimizer` | `9router/gh/gpt-4o-mini` | Meta analysis |
| `hermes-learning-coach` | `9router/gh/gpt-4o-mini` | Explanations |
| `browser-tester` | `9router/gh/gpt-4o-mini` | UI test scripts |

## Routing Decision Guide

```
Task requires web search?
  → researcher (codex)

Task is < 200 lines, single file?
  → cheap-coder (mini)

Task spans multiple files / complex logic?
  → senior-coder (codex)

Task involves auth, permissions, or secrets?
  → security-auditor (codex)

Task is architecture / design?
  → architect (codex)

Task is explaining / teaching?
  → hermes-learning-coach (mini)
```

## Checking Proxy Health

```bash
# Quick check
curl -s http://localhost:3000/health

# Full smoke test
bash ~/projects/nurse-agents/scripts/opencode/router-smoke-test.sh
```

## Proxy Not Running?

The proxy at port 3000 must be started manually (it does not autostart):

```bash
# Check if running
lsof -i :3000

# If One-API: typically started via Docker or systemd
# Check system-state.md for the exact start command
cat ~/.config/opencode/agent-notes/system-state.md | grep -A5 "oneapi"
```

## Registry File

`~/.config/opencode/profiles/registry.json` controls:
- Allowed file paths per agent
- Allowed domains for web requests
- Windows policy permissions
- MCP server aliases

Do not edit directly — changes here affect all agent permissions globally.
