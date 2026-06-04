# Architecture: OpenCode AI Stack

**Last updated:** 2026-06-04

## Overview

Hệ thống chạy trên 2 tầng: Windows host (tầng UI/apps) và Ubuntu WSL2 (tầng AI/dev).

```
┌─────────────────────────────────────────────────┐
│  WINDOWS HOST                                   │
│  - VSCode + Extensions                          │
│  - Docker Desktop (WSL2 backend)                │
│  - MCP Windows Bridge (windows-bridge.mjs)      │
│  - AutoHotkey / Desktop automation              │
└──────────────────┬──────────────────────────────┘
                   │ WSL2 / localhost bridge
┌──────────────────▼──────────────────────────────┐
│  UBUNTU WSL2                                    │
│                                                 │
│  OpenCode 1.15.13                               │
│  ├── 15 agent roles                             │
│  ├── 12 workflow commands                       │
│  ├── 11 skills                                  │
│  └── ~/.config/opencode/                        │
│                                                 │
│  Model Routing (port 3000)                      │
│  └── Anthropic-compatible proxy                 │
│      ├── 9router/cx/gpt-5.3-codex  (complex)   │
│      └── 9router/gh/gpt-4o-mini    (simple)    │
│                                                 │
│  Ollama (port 11434)                            │
│  └── 9 local models (llava, gemma4, etc.)      │
│                                                 │
│  MCP Servers (all disabled by default)          │
│  ├── github, postgres, mysql, browser           │
│  ├── scheduler, context7, grounded-docs         │
│  ├── memory, gitnexus, grafana-monitoring       │
│  └── cloudflare (remote)                        │
│                                                 │
│  nurse-agents project                           │
│  └── ~/projects/nurse-agents/                  │
└─────────────────────────────────────────────────┘
```

## Key Components

### OpenCode (`~/.config/opencode/`)
- `opencode.jsonc` — main config: agents, MCP, providers, permissions
- `agents/*.md` — 15 role definitions
- `commands/*.md` — 12 slash commands
- `skills/*/SKILL.md` — 11 reusable skill guides
- `healthchecks/` — system monitoring scripts
- `agent-notes/` — persistent memory across sessions
- `profiles/registry.json` — model routing and permission policies
- `mcp/windows-bridge.mjs` — Windows ↔ WSL2 MCP bridge

### Model Routing
| Route | Provider | Use case |
|---|---|---|
| `9router/cx/gpt-5.3-codex` | Via proxy port 3000 | Complex, multi-file, security |
| `9router/gh/gpt-4o-mini` | Via proxy port 3000 | Simple tasks, Q&A, boilerplate |
| `ollama-local/*` | localhost:11434 | Offline, local models |

### MCP Servers
All disabled by default. Enable per-session as needed:
- `github` — PR/issue management via `~/bin/github-mcp-server`
- `postgres` / `mysql` — database read access
- `browser` — web automation via Playwright
- `memory` — persistent cross-session memory at `~/.local/share/opencode/memory.jsonl`
- `gitnexus` — enhanced git operations
- `grafana-monitoring` — metrics dashboard
- `cloudflare` — remote MCP at `https://mcp.cloudflare.com/mcp`

### nurse-agents Project
FastAPI service at `~/projects/nurse-agents/`:
```
src/nurse_agents/
├── main.py          — FastAPI app, global exception handlers
├── config.py        — Settings via pydantic-settings
├── api/
│   ├── health.py    — GET /health
│   ├── diagnosis.py — POST /diagnosis/project-start, GET /diagnosis/{id}
│   └── schemas.py   — ErrorDetail, ErrorResponse, ErrorResponseWrapper
└── core/
    ├── models.py    — Pydantic models (DiagnosisResponse, ProjectDiagnosisResponse)
    └── advice.py    — build_project_start_diagnosis() business logic
```

## Data Flow: Diagnosis Request

```
Client
  │ POST /diagnosis/project-start
  ▼
FastAPI (main.py)
  │ Pydantic validation → 422 if invalid
  ▼
diagnose_project_start() (diagnosis.py)
  │ build_project_start_diagnosis(payload)
  ▼
build_project_start_diagnosis() (advice.py)
  │ returns DiagnosisResponse
  ▼
UUID generated → stored in _diagnosis_storage
  │
  ▼ ProjectDiagnosisResponse (with project_id)
Client ← 200 OK
```

## Runtime State Locations
- OpenCode auth/sessions: `~/.local/share/opencode/`
- Agent memory notes: `~/.config/opencode/agent-notes/`
- Health reports: `~/.config/opencode/healthchecks/reports/`
- Project backups: `~/backups/opencode/`
