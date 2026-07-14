# MCP Policy

**Last updated:** 2026-06-04

Quy tắc sử dụng MCP servers trong OpenCode cho dự án nurse-agents.

---

## Nguyên tắc: Tất cả MCP disabled theo mặc định

MCP servers chỉ nên enable khi thực sự cần cho task hiện tại. Enable không cần thiết:
- Tốn token context
- Tăng attack surface
- Chậm startup

---

## MCP Servers Có Sẵn

| Server | Khi nào enable | Lưu ý |
|---|---|---|
| `github` | PR review, issue management | Cần `GITHUB_TOKEN` env var |
| `postgres` | Đọc/phân tích database | Read queries only, không INSERT/UPDATE/DELETE |
| `mysql` | Đọc/phân tích MySQL | Read queries only |
| `browser` | Playwright web testing, UI automation | Cần browser-tester agent |
| `memory` | Lưu memory cross-session | Lưu tại `~/.local/share/opencode/memory.jsonl` |
| `gitnexus` | Git operations nâng cao | Dùng thay github khi không cần PR |
| `grafana-monitoring` | Đọc metrics, dashboards | Read-only |
| `scheduler` | Cron jobs, scheduled tasks | Dùng với automation-planner |
| `context7` | Library documentation | Dùng với researcher |
| `grounded-docs` | Document search | Dùng với researcher |
| `cloudflare` | Cloudflare API | Remote MCP, cần auth |
| `windows-bridge` | Windows ↔ WSL2 bridge | Tự động qua `windows-bridge.mjs` |

---

## Cách Enable MCP cho Một Session

Thêm vào `opencode.jsonc` hoặc dùng project-level config:

```json
{
  "mcp": {
    "github": {
      "disabled": false
    }
  }
}
```

Sau khi enable, restart OpenCode để load.

---

## Database MCP Rules (Critical)

**KHÔNG BAO GIỜ** để agent chạy:
- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE` qua MCP
- Migrations tự động qua MCP
- Schema changes không có approval

Chỉ dùng `db-analyst` và `db-readonly` agents với database MCP — cả 2 agents này bị giới hạn read-only ở cấp permission.

---

## Windows Bridge

`windows-bridge.mjs` cho phép OpenCode trên WSL2 gọi tools trên Windows host (AutoHotkey, desktop UI, etc.).

File: `~/.config/opencode/mcp/windows-bridge.mjs`

Policies:
- `ahk_input`: allow (AutoHotkey input)
- `window_focus`: allow
- Desktop operations: follow `~/.config/opencode/profiles/registry.json` `windows_policies`

---

## Debugging MCP

```bash
# Quick check
bash ~/projects/nurse-agents/scripts/opencode/mcp-healthcheck.sh

# Or use the skill
/mcp-health

# Detailed debugging → use mcp-debugging skill
```

Xem thêm: [mcp-debugging skill](../../../.config/opencode/skills/mcp-debugging/SKILL.md)

---

## Security Rules for MCP

1. **GitHub MCP**: Không post comments hay close issues mà không có user confirmation
2. **Database MCP**: Chỉ SELECT — nếu cần write, dùng migration scripts được review
3. **Browser MCP**: Không login vào production services
4. **Cloudflare MCP**: Cần explicit user approval trước mỗi write operation
5. **Scheduler MCP**: Không tạo cron jobs mà không review schedule và command
