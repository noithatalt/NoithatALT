# Source of Truth — nurse-agents + OpenCode

**Last updated:** 2026-07-11 (V7 Phase A — docs backfill)  
**Migration Note:** OpenHands → Agent-Canvas (2026-06-07). See [AGENT_CANVAS_MIGRATION.md](AGENT_CANVAS_MIGRATION.md)

File này là điểm vào ngắn nhất để biết cần đọc file nào trước. Không đọc toàn bộ docs nếu task không cần.

---

## Mục tiêu tổng thể

> Xây dựng OpenCode stack có khả năng thay thế claude.ai cho team nội bộ:
> chat agent + knowledge base (Arkon) + monitoring + multi-provider LLM,
> chạy hoàn toàn on-premise.
>
> **Quy tắc:** KHÔNG xóa / KHÔNG bỏ thứ gì đang có. Chỉ BUILD THÊM. Nếu cần xóa → HỎI TRƯỚC.

### So sánh với claude.ai

| Tính năng | claude.ai | Stack hiện tại | Trạng thái |
|---|---|---|---|
| Chat agent (TUI/CLI/Web) | ✅ | OpenCode v1.15.13 | ✅ DONE |
| Multi-model routing | ✅ | 9router → One-API → Anthropic/OpenAI | ✅ DONE |
| Local models (offline) | ❌ | Ollama 9 models | ✅ DONE (hơn claude.ai) |
| Agent roles (15+) | ✅ Projects | 15 agents + 11 skills | ✅ DONE |
| Knowledge base | ✅ Projects KB | Arkon (27 pages + monitoring) | ✅ DONE |
| Tool use / MCP | ✅ | 12 MCP servers (disabled mặc định) | ⚠️ Có, cần bật |
| Session + memory | ✅ | SQLite + agent-notes | ✅ DONE |
| Monitoring pipeline | ❌ | Netdata + GLPI + systemd timer | ✅ DONE (hơn claude.ai) |
| Artifacts / preview | ✅ | ❌ Chưa có | 🔴 Thiếu |
| Web search tự động | ✅ | MCP researcher (manual) | 🟡 Cần bật mặc định |
| Web UI | ✅ | `opencode web` | ✅ DONE |
| Image vision | ✅ | Ollama llava | ✅ DONE |

### Khoảng cách còn lại (ưu tiên build thêm)
1. **Artifacts** — preview code/diagram trong UI → opencode web renderer
2. **Web search mặc định** — enable researcher MCP mặc định
3. **Projects UI** — Arkon đang giải quyết phần knowledge base

---

## Khi cần bắt đầu nhanh

→ Đọc [START_HERE.md](../../START_HERE.md)

## Khi cần hiểu hệ thống AI stack

→ Đọc [architecture.md](architecture.md)  
→ Config thực tế: `~/.config/opencode/opencode.jsonc`

## Khi cần chọn agent đúng

→ Đọc [agent-team.md](agent-team.md)

## Khi cần biết workflow chuẩn

→ Đọc [workflow-policy.md](workflow-policy.md)

## Khi cần biết model routing

→ Đọc [model-routing.md](model-routing.md)

## Khi cần kiểm tra hệ thống

```bash
bash ~/projects/nurse-agents/scripts/opencode/full-healthcheck.sh
```
→ Chi tiết: [healthcheck-policy.md](healthcheck-policy.md)

## Khi cần rollback

→ Đọc [rollback.md](rollback.md)

## Khi gặp vấn đề MCP

→ Đọc [mcp-policy.md](mcp-policy.md)  
→ Hoặc dùng skill: `mcp-debugging`

## Khi cần audit security

→ Dùng: `/security-check`  
→ Skill: `security-review`

## Khi cần học / hiểu code

→ Agent: `hermes-learning-coach` (internal, có thể delegate)  
→ Agent: `nous-hermes` (external advisor, read-only — xem [nous-hermes-policy.md](nous-hermes-policy.md))  
→ Skill: `ai-learning`

## Khi cần setup Agent-Canvas (AI coding agent)

→ Đọc: [AGENT_CANVAS_MIGRATION.md](AGENT_CANVAS_MIGRATION.md)  
→ Quick Start: `npm install -g @openhands/agent-canvas && agent-canvas`  
→ Web UI: http://localhost:8000

---

## Trạng thái hệ thống hiện tại

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| OpenCode | ✅ v1.17.15 | 18 agents, ~36 commands, 23 skills, serve :22000 (systemd opencode-hooks, fix 22/06) |
| MCP servers | ✅ 4/14 enabled | memory, filesystem (~/projects only), sequential-thinking, windows-bridge (framing fix 05/07); cloudflare disabled chờ OAuth |
| Permission gate | ⚠️ V6.4 rules | read_whitelist gồm /mnt/c-f; live-verify a–k còn treo; nghi vấn #7006 permission.ask không trigger → xử lý ở V7 Phase C |
| Nous Hermes | ✅ v0.16.0 "bộ não" | `~/.hermes/`, 2 profiles (telegram/coach), model HN, bridge :18790 systemd (queue drain 60s), gateway systemd (cron+hooks), 2 cron jobs (memory digest 08:00, healthcheck 07:30), skills custom, dashboard on-demand `hermes dashboard` :9119 |
| 9router :20128 | ✅ chạy | LLM routing chính (One-API DEPRECATED từ V3, xác nhận 22/06) |
| Ollama port 11434 | ✅ chạy | 10 models |
| nurse-agents API | ✅ | 80 tests pass, SQLite persistent |
| Agent-Canvas | ✅ port 8000 | npm agent-canvas, LLM: 9router kr/claude-sonnet-4-agentic, workspace /tmp/oh-test-workspace |

**Cập nhật trạng thái này** khi có thay đổi lớn về infrastructure.

---

## Arkon Data Ingestion Rule (V2.1.1)

Wazuh, Netdata, and GLPI MUST NOT send data directly to Arkon.

Only `arkon-summary-reporter` is allowed to send summarized reports to Arkon.

Allowed flow:
```
Wazuh / Netdata / GLPI
  -> local logs / local dashboards / local reports
  -> sanitizer -> validator -> content-moderator -> approval-gate
  -> arkon-summary-reporter
  -> Arkon
```

Direct push, direct webhook, direct API sync, or raw log forwarding
from Wazuh, Netdata, or GLPI to Arkon is FORBIDDEN.

---

## Wazuh RAM-Blocked Status (V2.1.1)

Wazuh is currently RAM-BLOCKED and must remain DISABLED.

```
Wazuh status: DISABLED / RAM-BLOCKED / DEFERRED
```

Reason: Wazuh stack requires 6-10 GB RAM. Current WSL2 RAM is 15.6 GB shared
with Windows host. Running Wazuh alongside OpenHands, One-API, Ollama, and
nurse-agents API would push usage above WARN threshold (70%) or FAIL (85%).

Phase C (Wazuh lab) is DEFERRED until:
1. Additional RAM provisioned, OR
2. Isolated resource environment confirmed.

Active fallback mode:
- Netdata local-only (when installed)
- GLPI local-only (when installed)
- Basic healthcheck scripts
- Manual security log review
- arkon-summary-reporter summary-only

Phase 10 structure is preserved. Operating mode = lightweight fallback.
