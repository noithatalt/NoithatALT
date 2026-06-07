# Current State Audit

**Audit date:** 2026-06-04 | **Host:** Windows i7-14700K 32GB + Ubuntu WSL2
**Stack version:** V1 + V2 + V2.1 DONE | **Tests:** 72/72 PASS

## Infrastructure

| Service | Port | Bind | Trạng thái | Ghi chú |
|---|---:|---|---|---|
| Agent-Canvas | 8000 | 127.0.0.1 | npm, Up | AI coding agent — port 18000 backend, 3001 frontend |
| One-API | 3000 | 127.0.0.1 | Docker, Up | Model proxy backend — không public |
| 9router | 20128 | 0.0.0.0 | PM2, Up | Gateway; public qua `claude.noithatalt.io.vn` |
| Ollama | 11434 | 127.0.0.1 | Up | 9 local models |
| nurse-agents API | 8000 | localhost | Up khi `make run` | FastAPI, SQLite |
| cloudflared | — | WSL canonical | Up | Tunnel chính — `/etc/cloudflared/config.yml` |
| n8n | 5678 | localhost | Up | Cần auth; public qua `n8n.noithatalt.io.vn` |

**Public qua Cloudflare (có chủ đích):**

| Hostname | Backend |
|---|---|
| `n8n.noithatalt.io.vn` | `localhost:5678` — cần auth |
| `claude.noithatalt.io.vn` | `localhost:20128` — 9router gateway |

**Tuyệt đối KHÔNG public:** Wazuh, Netdata, GLPI, Agent-Canvas, One-API, Ollama, nurse-agents API.

## AI Tools

| Tool | Path | Vai trò |
|---|---|---|
| OpenCode v1.15.13 | `~/.local/bin/opencode` | Runtime chính |
| Claude Code | `~/.npm-global/bin/claude` | Builder chính |
| Codex CLI | `~/.npm-global/bin/codex` | Builder CLI |
| Aider | `~/.local/bin/aider` | Diff fixer |
| Agent-Canvas | npm, port 8000 | AI coding agent (npm install -g @openhands/agent-canvas) |

## Ollama Models (9 total)

| Model | Size | Dùng cho |
|---|---:|---|
| llama3.1:8b | 4.9 GB | General |
| qwen2.5:7B | 4.7 GB | General |
| qwen2.5-coder:7B | 4.7 GB | Code |
| deepseek-r1:7B | 4.7 GB | Reasoning |
| qwen3.5:9b | 6.6 GB | Strong general |
| gemma4:latest | 9.6 GB | Strong |
| llava:latest | 4.7 GB | Vision |
| moondream:latest | 1.7 GB | Vision (nhẹ) |
| nomic-embed-text | 957 MB | Embedding |

## Model Routing

```
9router/cx/gpt-5.3-codex  → hard/senior tasks (architect, security, refactor)
9router/gh/gpt-4o-mini    → medium/cheap tasks (planner, cheap-coder, research)
Ollama llava / moondream  → vision tasks (local, FREE)
Ollama qwen3.5:9b         → fallback medium local
```

One-API (3000) là proxy backend. 9router (20128) là gateway chính.

## Agent Stack (17 agents)

| Agent | Cấp | Model | Vai trò |
|---|---|---|---|
| `automation-planner` | Primary | gpt-4o-mini | Điều phối plan/task |
| `architect` | Primary/Sub | gpt-5.3-codex | Thiết kế kiến trúc lớn |
| `devops` | Primary/Sub | gpt-5.3-codex | Docker, tunnel, service, healthcheck |
| `hermes-learning-coach` | Support | gpt-4o-mini | Learning/memory có kiểm soát |
| `security-auditor` | Gate | gpt-5.3-codex | Audit bảo mật trước outbound send |
| `caveman` | Gate | gpt-4o-mini | Gate chống over-engineering |
| `content-moderator` | Gate | gpt-4o-mini | Kiểm duyệt payload outbound (V2.1) |
| `reviewer` | Gate/Sub | gpt-5.3-codex | Review code/diff |
| `senior-coder` | Sub | gpt-5.3-codex | Code khó, refactor |
| `cheap-coder` | Sub | gpt-4o-mini | Fix nhỏ, docs |
| `researcher` | Sub | gpt-4o-mini | Tra cứu tài liệu |
| `cost-optimizer` | Support | gpt-4o-mini | Kiểm soát chi phí token |
| `db-analyst` | Sub | gpt-5.3-codex | DB read-only |
| `browser-tester` | Sub | gpt-4o-mini | Test UI/browser |
| `planner` | Legacy | — | Trùng automation-planner |
| `coder` | Legacy | — | Trùng cheap/senior-coder |
| `db-readonly` | Legacy | — | Trùng db-analyst |

## Commands (12)

```
/plan              → automation-planner
/review-plan       → reviewer + security-auditor + caveman
/implement         → automation-planner → cheap/senior-coder
/code-review       → reviewer + security-auditor
/security-check    → security-auditor + devops
/verify            → reviewer + devops + browser-tester
/agent-health      → devops
/mcp-health        → devops
/router-test       → devops + cost-optimizer
/cost-report       → cost-optimizer
/create-issue      → automation-planner
/review-pr         → reviewer + security-auditor
```

## Skills (12)

```
workflow-plan       review-plan        code-review
security-review     security-audit     mcp-debugging
ai-learning         cost-optimization  role-audit
bugfix-workflow     feature-workflow   caveman-gate
```

## MCP Servers (12)

```
github              postgres           mysql
browser             scheduler          context7
grounded-docs       memory             gitnexus
windows-bridge      grafana-monitoring cloudflare
```

## nurse-agents API

- 6 endpoints: POST/GET-list/GET/PUT/DELETE diagnosis + GET health
- SQLite: `nurse_agents.db`
- Tests: **72 passed** (venv: `make setup && make test`)

## Arkon Pipeline (V2.1)

```
build_summary → redact_summary → validate_summary → moderate_summary → approval_gate → send_summary
```

Xem [failure-mode.md](failure-mode.md) và [arkon-reporting-policy.md](arkon-reporting-policy.md).
