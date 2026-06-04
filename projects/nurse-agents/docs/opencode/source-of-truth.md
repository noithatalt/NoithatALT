# Source of Truth — nurse-agents + OpenCode

**Last updated:** 2026-06-04

File này là điểm vào ngắn nhất để biết cần đọc file nào trước. Không đọc toàn bộ docs nếu task không cần.

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

→ Agent: `hermes-learning-coach`  
→ Skill: `ai-learning`

---

## Trạng thái hệ thống hiện tại

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| OpenCode | ✅ v1.15.13 | 15 agents, 12 commands, 11 skills |
| Proxy port 3000 | ✅ chạy | Anthropic-compatible |
| Ollama port 11434 | ✅ chạy | 9 models |
| nurse-agents API | ✅ | 15 tests pass, SQLite persistent |
| MCP servers | ⚠️ disabled mặc định | Enable per task |
| OpenHands | ✅ port 3001 | docker run, workspace ~/openhands-workspace |

**Cập nhật trạng thái này** khi có thay đổi lớn về infrastructure.
