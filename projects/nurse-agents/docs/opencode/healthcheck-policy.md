# Healthcheck Policy

**Last updated:** 2026-06-04

---

## Khi nào chạy healthcheck

| Tình huống | Check cần chạy |
|---|---|
| Bắt đầu phiên làm việc mới | `agent-healthcheck.sh` |
| Sau khi sửa `opencode.jsonc` | `audit-current-state.sh` |
| MCP tools không xuất hiện | `mcp-healthcheck.sh` |
| Agent trả lời kỳ lạ / lỗi model | `router-smoke-test.sh` |
| Trước khi demo hoặc deploy | `full-healthcheck.sh` |
| Sau khi cài thêm agent/skill mới | `audit-current-state.sh` |

---

## Scripts

Tất cả ở `~/projects/nurse-agents/scripts/opencode/`:

```bash
# Chạy tất cả (recommended trước demo)
bash scripts/opencode/full-healthcheck.sh

# Chạy từng phần
bash scripts/opencode/agent-healthcheck.sh      # validate agent frontmatter
bash scripts/opencode/audit-current-state.sh    # so sánh expected vs actual
bash scripts/opencode/mcp-healthcheck.sh        # MCP connectivity
bash scripts/opencode/router-smoke-test.sh      # proxy port 3000
bash scripts/opencode/permission-smoke-test.sh  # agent permissions
```

---

## Automated Healthchecks (OpenCode Autopilot)

OpenCode có hệ thống autopilot tại `~/.config/opencode/healthchecks/`:

| Script | Chức năng |
|---|---|
| `run-infra.mjs` | Check Docker, WSL2, ports |
| `run-mcp.mjs` | Check MCP server config |
| `run-runtime.mjs` | Check OpenCode runtime state |
| `run-system.mjs` | Check system resources |
| `run-autopilot.mjs` | Orchestrate tất cả checks |

Reports lưu tại: `~/.config/opencode/healthchecks/reports/`

Xem status mới nhất:
```bash
cat ~/.config/opencode/healthchecks/reports/autopilot-latest.json 2>/dev/null | python3 -m json.tool | head -30
```

---

## Backup Trước Khi Sửa Config

**Bắt buộc** backup trước khi sửa `opencode.jsonc` hoặc agent files:

```bash
bash scripts/opencode/backup-opencode-config.sh
```

Backup lưu tại `~/backups/opencode/`, giữ 5 bản gần nhất.

---

## Thresholds

| Metric | Warning | Critical |
|---|---|---|
| Agents với frontmatter lỗi | > 0 | > 2 |
| Commands thiếu | > 0 | > 3 |
| Proxy không phản hồi | > 3s | không kết nối |
| Tests fail | bất kỳ | bất kỳ |

---

## Nếu Full Healthcheck Fail

1. Xác định check nào fail (đọc output)
2. Chạy riêng script đó để xem chi tiết
3. Tham khảo skill phù hợp (`/mcp-health`, `/router-test`, `/agent-health`)
4. Nếu không fix được: `opencode researcher` với error message cụ thể
