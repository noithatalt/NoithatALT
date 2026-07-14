# OpenCode Build Summary — Tổng kết toàn bộ quá trình

**Cập nhật:** 2026-06-10 | **Tests:** 80/80 PASS | **Version:** V4 — Agentic Layer (project-context, skills, memory, task-tracker, checkpoint/resume)

---

## 1. Những gì đã hoàn thành

| Phase | Mô tả | Kết quả |
|---|---|---|
| **V1** | OpenCode stack: 17 agents, 12 commands, 12 skills, 12 MCP servers | ✅ DONE |
| **A (V2)** | 14 policy docs: arkon, security, data-classification, retention, failure-mode... | ✅ DONE |
| **B (V2)** | Arkon pipeline: build→redact→validate→dry-run→send | ✅ DONE |
| **A+B (V2.1)** | +3 docs, moderate_summary.py, approval_gate.py, 17 tests mới | ✅ DONE |
| **V2.1.1** | security-policy.md, RAM policy, Wazuh deferred chính thức | ✅ DONE |
| **D** | Netdata local Docker (port 127.0.0.1:19999, 7/7 PASS) | ✅ DONE |
| **E** | Arkon gửi thật: 6/6 PASS, HTTP 200, .env.pipeline live | ✅ DONE |
| **E.1** | Arkon embedding: Ollama nomic-embed-text-v2-moe (768d, local, free) | ✅ DONE |
| **F** | GLPI local: load_glpi_tickets.py, PII masking, 8 tests PASS | ✅ DONE |
| **H** | Scheduled pipeline: systemd timer hourly, .env.pipeline auto-loaded | ✅ DONE |
| **SX** | File SX cũ (E:\) → Arkon KB: 27 wiki pages, 50 KH, 2828 files, 816 MB | ✅ DONE |
| **Nous Hermes** | Tích hợp Nous Research Hermes làm learning/advisor layer (read-only, song song với hermes-learning-coach) | ✅ DONE |
| **Arkon MCP** | Claude Code kết nối Arkon KB qua MCP — project scope, token gitignored, 27 wiki pages queryable. Fix bug `search_wiki` (`project_ids` → `None`), rebuild image | ✅ DONE |
| **V3 — 9router fix** | Cập nhật API key mới `sk-fded719835aff07c`; fix Opencode combo self-reference (loop → "No active credentials"); xóa provider oneapi/xiaomi stale | ✅ DONE |
| **V3 — VSCode ext fix** | Extension `local.opencode-vscode-panel-0.1.1`: sửa path `.npm-global` → `.local/bin/opencode` (v1.16.2), `wsl.exe -e` → `wsl.exe --` (TTY fix), thêm 500ms delay | ✅ DONE |
| **V3 — SwarmClaw** | SwarmClaw v1.9.37 tích hợp vào stack: fix SW combo self-ref, update agent model `cx/gpt-5.4`→`SW`, systemd service `:3456`, agent `swarm-orchestrator` trong opencode.json | ✅ DONE |
| **V3 — Agent-Canvas** | Giữ lại `@openhands/agent-canvas` v1.0.0-rc.5 (`:8000`) — on-demand, không chạy thường xuyên, không xung đột SwarmClaw | ✅ DONE |

**Tổng tests:** 80/80 PASS

---

## 2. Những gì còn cần bổ sung

| Phase | Mô tả | Điều kiện |
|---|---|---|
| **C** | Wazuh local lab (Docker single-node) | **DEFERRED** — nâng RAM WSL2; certs sẵn tại `docker/wazuh/`; compose sẵn tại `docker/wazuh-compose.yml` |
| **C.2** | Windows Wazuh agent | Phụ thuộc Phase C |
| **G** | LangChain agent + Wazuh active response + FIDO2 auth | **Để sau** |

---

## 3. Sơ đồ hoạt động

### 3.1 — AI Stack tổng thể (V3)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          WINDOWS HOST                                   │
│                       (Người dùng làm việc)                             │
│                                                                         │
│   VS Code ──────────────────────────── Editor / Claude Code VSCode ext  │
│   Browser → http://localhost:3119       Arkon KB UI                     │
│   Browser → http://localhost:3456       SwarmClaw Web UI  ← V3 MỚI      │
│   Browser → http://localhost:8000       Agent-Canvas (on-demand)        │
│   Browser → https://claude.noithatalt.io.vn  9router public endpoint   │
│                                                                         │
│   [Approve] approval-result.json ──── AI submit → user approve          │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ WSL2  (windows-bridge MCP)
┌───────────────────────────────▼─────────────────────────────────────────┐
│                           Ubuntu WSL2  (AI làm việc)                    │
│                                                                         │
│  ┌──────────────────────┐  ┌───────────────────┐                        │
│  │  RUNTIME CHÍNH       │  │  MAIN BUILDER     │                        │
│  │  OpenCode v1.16.2    │  │  Claude Code CLI  │                        │
│  │  TUI/VSCode          │  │  (xây dựng stack) │                        │
│  └──────────┬───────────┘  └────────┬──────────┘                        │
│             └──────────────┬─────────┘                                  │
│                            ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │        9router :20128 — Cổng gọi AI trung tâm (systemd)         │  │
│  │  Combos: Opencode / SW / openclaw / HN                          │  │
│  └──────┬────────────────┬──────────────────┬───────────────────────┘  │
│         │                │                  │                          │
│  ┌──────▼──────┐  ┌──────▼──────┐  ┌───────▼──────┐  ┌─────────────┐ │
│  │ TRÍ NHỚ+   │  │ GATEWAY+    │  │ ĐIỀU PHỐI   │  │ LOCAL       │ │
│  │ COACH       │  │ TOOLS+      │  │ AGENT NỀN   │  │ FALLBACK    │ │
│  │ Hermes      │  │ KÊNH VÀO/RA │  │ SwarmClaw   │  │ Ollama      │ │
│  │ :18790 PM2  │  │ OpenClaw    │  │ :3456 svc   │  │ :11434      │ │
│  │ reasoning   │  │ :18789 svc  │  │ web UI      │  │ embedding   │ │
│  └─────────────┘  └──────┬──────┘  └─────────────┘  └─────────────┘ │
│                           │ (Zalo Collector → OpenClaw)               │
│  ┌────────────────────────────────────────────────────────────────┐   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Arkon Knowledge Base  :5055 / :3119                 │  │
│  │  PostgreSQL+pgvector │ Redis │ MinIO │ Worker │ Frontend         │  │
│  │  Embedding: Ollama nomic-embed-text-v2-moe (local, free)         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  nurse-agents pipeline (systemd timer — hourly)                  │  │
│  │  Netdata :19999 + GLPI → build→redact→validate→moderate→send    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Zalo Collector (systemd)  │  n8n :5678 (Cloudflare tunnel)     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Agent-Canvas :8000 (on-demand) — OpenHands web UI               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘

Cloudflare Tunnel (public):
  claude.noithatalt.io.vn  →  9router :20128
  n8n.noithatalt.io.vn     →  n8n :5678 (auth)
```

### 3.2 — Arkon Monitoring Pipeline (tự động, hourly)

```
┌──────────────────────────────────────────────────────────────────┐
│  DATA SOURCES (local only, không public)                         │
│                                                                  │
│  Netdata :19999  ──────────────────────┐                         │
│  GLPI (local)    ──────────────────────┤                         │
│  Wazuh :55000    ── DEFERRED ──────────┤                         │
└────────────────────────────────────────┼─────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  PIPELINE (scripts/arkon/)   [systemd timer — hourly]            │
│                                                                  │
│  1. build_summary.py     → summary.json                          │
│  2. redact_summary.py    → summary-redacted.json  (xóa PII)      │
│  3. validate_summary.py  → schema check, exit 1 nếu fail         │
│  4. moderate_summary.py  → PASS / BLOCK / NEED_APPROVAL          │
│  5. approval_gate.py     → đọc approval-result.json              │
│  6. send_summary.py      → multipart upload, JWT, retry ×3       │
└────────────────────────────────────────┬─────────────────────────┘
                                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  Arkon Knowledge Base  :5055 (API) / :3119 (UI)                  │
│  Embedding: Ollama nomic-embed-text-v2-moe (768d, local, free)   │
│  LLM: 9router → Claude Sonnet 4.6                               │
│                                                                  │
│  KB hiện có:                                                     │
│  ├── Monitoring summaries (Netdata + GLPI — hourly)              │
│  └── File SX Index — 27 pages, 50 KH, 2828 files, 816 MB        │
└──────────────────────────────────────────────────────────────────┘
```

### 3.3 — SX Pipeline (on-demand)

```
E:\File SX cũ\ (Windows)
        │  mount WSL2: /mnt/e/File SX cũ/
        ▼
build_sx_summary.py   → quét metadata 50 thư mục KH (tên, size, loại file)
        │                 KHÔNG đọc nội dung DXF/NC/SKP
        ▼
redact_summary.py     → xóa path tuyệt đối, IP, secret
        ▼
validate (inline)     → schema check, secrets_included=false
        ▼
moderate_summary.py   → NEED_APPROVAL (có path-like string)
        ▼
approval-result-sx.json  ← người dùng tạo trên Windows
        ▼
upload multipart → Arkon :5055  →  27 wiki pages indexed
```

### 3.4 — Fail-closed chain

```
sanitizer fail  ──►  STOP — không gọi validator
validator fail  ──►  STOP — không gọi moderator
moderator BLOCK ──►  STOP — không gọi approval gate
approval fail   ──►  STOP — không gửi gì
send fail ×3    ──►  queue local — không retry vô hạn
```

---

## 4. Bảng vận hành

### 4.1 — Kiểm tra hệ thống hàng ngày

| Lệnh | Mục đích |
|---|---|
| `bash ~/projects/nurse-agents/scripts/monitoring/check-netdata.sh` | Netdata 7 checks |
| `bash ~/projects/nurse-agents/scripts/monitoring/check-pipeline.sh` | Pipeline 7 checks |
| `bash ~/projects/nurse-agents/scripts/monitoring/check-ram-policy.sh` | RAM — đủ chạy Wazuh? |
| `docker ps` | Containers đang chạy |
| `journalctl --user -u nurse-agents-pipeline --since today` | Log pipeline hôm nay |

### 4.2 — Monitoring pipeline (thủ công)

| Lệnh | Mục đích |
|---|---|
| `bash scripts/arkon/run_pipeline.sh --dry-run` | 4 stages đầu, không gửi |
| `bash scripts/arkon/run_pipeline.sh` | Đến moderate → tạo approval-request.json rồi dừng |
| `bash scripts/arkon/run_pipeline.sh --auto` | Full 6 stages, dùng approval-result.json sẵn |

### 4.3 — SX pipeline (on-demand)

| Lệnh | Mục đích |
|---|---|
| `bash scripts/arkon/run_sx_pipeline.sh --dry-run` | Scan + validate, không gửi |
| `bash scripts/arkon/run_sx_pipeline.sh` | Tạo approval-request-sx.json rồi dừng |
| `bash scripts/arkon/send_sx_now.sh` | Interactive — hỏi password, gửi thật lên Arkon |

### 4.4 — Quy trình approve và gửi (monitoring)

```
1. bash run_pipeline.sh
   → tạo: reports/arkon/approval-request.json

2. Người dùng tạo trên Windows:
   reports/arkon/approval-result.json
   {
     "approved": true,
     "scope": "send_arkon_summary",
     "approved_by": "admin",
     "approved_at": "2026-06-04T12:00:00+00:00"
   }

3. bash run_pipeline.sh --auto  →  HTTP 200 → Arkon
```

### 4.5 — Timer systemd

| Lệnh | Mục đích |
|---|---|
| `systemctl --user status nurse-agents-pipeline.timer` | Trạng thái timer |
| `systemctl --user list-timers` | Tất cả timers + lần chạy kế tiếp |
| `systemctl --user enable --now nurse-agents-pipeline.timer` | Bật (đã bật) |
| `systemctl --user disable nurse-agents-pipeline.timer` | Tắt tạm |
| `systemctl --user start nurse-agents-pipeline.service` | Chạy ngay (không chờ timer) |

### 4.6 — Tests

| Lệnh | Mục đích |
|---|---|
| `cd ~/projects/nurse-agents && python3 -m pytest tests/ -q` | Toàn bộ 80 tests |
| `python3 -m pytest tests/test_sx_pipeline.py -v` | 8 tests SX pipeline |
| `python3 -m pytest tests/test_content_moderation.py -v` | Content moderator |
| `python3 -m pytest tests/test_authenticator_gate.py -v` | Approval gate |

### 4.7 — Arkon services

| Lệnh | Mục đích |
|---|---|
| `docker ps \| grep arkon` | Containers Arkon |
| `curl http://localhost:5055/health` | Health check API |
| `cd ~/projects/arkon && docker compose restart api` | Restart API |
| Browser: `http://localhost:3119` | Arkon UI — query KB |

### 4.8.1 — Arkon MCP (Claude Code)

| Lệnh | Mục đích |
|---|---|
| `claude mcp list` | Xem trạng thái MCP servers |
| `cd ~/projects/arkon && claude` | Mở session Claude Code — approve MCP lần đầu |
| `cd ~/projects/arkon && docker compose build api && docker compose up -d api` | Rebuild sau khi sửa source |
| MCP token: lấy mới mỗi lần restart qua `POST /api/my/mcp-token` | Token cũ hết hiệu lực sau rebuild |

**Scope:** project — ghi vào `~/projects/arkon/.mcp.json`, không ảnh hưởng global.  
**Lấy token mới:**
```bash
TOKEN=$(curl -s -X POST http://localhost:5055/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@arkon.local","password":"Luantam@92"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
MCP_TOKEN=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:5055/api/my/mcp-token -H "Content-Type: application/json" -d '{}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
cd ~/projects/arkon && claude mcp remove arkon; claude mcp add-json arkon \
  "{\"type\":\"http\",\"url\":\"http://localhost:5055/mcp\",\"headers\":{\"Authorization\":\"Bearer $MCP_TOKEN\"}}" \
  --scope project
```
**Bug đã fix:** `search_wiki` lỗi `'ResolvedIdentity' object has no attribute 'project_ids'` — fixed tại `app/mcp/tools.py:261,520` (`proj_uuids = None`).

### 4.8.2 — SwarmClaw (V3 — tích hợp 2026-06-09)

| Lệnh | Mục đích |
|---|---|
| `systemctl --user status swarmclaw` | Trạng thái SwarmClaw |
| `systemctl --user restart swarmclaw` | Restart sau update |
| `curl http://localhost:3456/api/health` | Health check (cần login → 401 = OK) |
| Browser: `http://localhost:3456` | SwarmClaw Web UI — quản lý agent/task/schedule |
| `@swarm-orchestrator` trong OpenCode | Dùng SwarmClaw model qua 9router/SW |

**Files liên quan:**
- Service: `~/.config/systemd/user/swarmclaw.service`
- Data: `~/.swarmclaw/data/swarmclaw.db` — agents, tasks, schedules
- Build: `~/.swarmclaw/builds/package-1.9.37/.next/standalone/server.js`
- Default agent model: `SW` (9router combo → `claude-haiku-4.5` / `gemini-3-flash`)

**Agent-Canvas (on-demand):**
```bash
cd ~/.npm-global/lib/node_modules/@openhands/agent-canvas && npx agent-canvas
# hoặc:
agent-canvas  # nếu đã add vào PATH
```
Port: `:8000`. Dùng khi cần OpenHands UI riêng biệt.

### 4.9 — Wazuh (khi nâng RAM xong)

```bash
# 1. Kiểm tra RAM đủ (> 8GB free)
bash ~/projects/nurse-agents/scripts/monitoring/check-ram-policy.sh

# 2. Tắt Ollama heavy model nếu đang chạy
ollama stop gemma4 || ollama stop qwen3.5:9b

# 3. Sửa wazuh-compose.yml — thêm volume mount certs:
#    - docker/wazuh/wazuh-certificates/node-1.pem → /etc/wazuh-indexer/certs/indexer.pem
#    - (xem docker/wazuh/wazuh-certificates/ để lấy đúng tên file)

# 4. Start stack
cd ~/projects/nurse-agents
docker compose -f docker/wazuh-compose.yml --env-file docker/monitoring/.env up -d

# 5. Đợi ~2 phút, kiểm tra
bash ~/projects/nurse-agents/scripts/monitoring/check-wazuh.sh

# 6. Tắt khi xong audit
docker compose -f docker/wazuh-compose.yml down
```

---

## 5. Cấu trúc file quan trọng

```
~/projects/nurse-agents/
├── scripts/
│   ├── arkon/
│   │   ├── run_pipeline.sh          ← Monitoring orchestrator (hourly)
│   │   ├── run_sx_pipeline.sh       ← SX orchestrator (on-demand)
│   │   ├── send_sx_now.sh           ← SX interactive send (hỏi password)
│   │   ├── build_summary.py         ← Stage 1: Netdata + GLPI + Wazuh
│   │   ├── build_sx_summary.py      ← Stage 1 SX: scan E:\File SX cũ\
│   │   ├── redact_summary.py        ← Stage 2: xóa PII/secret
│   │   ├── validate_summary.py      ← Stage 3: schema check
│   │   ├── moderate_summary.py      ← Stage 4: content moderation
│   │   ├── approval_gate.py         ← Stage 5: human approve
│   │   ├── send_summary.py          ← Stage 6: upload Arkon + retry
│   │   └── load_glpi_tickets.py     ← Helper: GLPI ticket pull
│   └── monitoring/
│       ├── check-pipeline.sh        ← Smoke test pipeline (7 checks)
│       ├── check-netdata.sh         ← Smoke test Netdata (7 checks)
│       ├── check-ram-policy.sh      ← RAM healthcheck
│       └── check-wazuh.sh           ← Smoke test Wazuh (khi bật)
├── tests/                           ← 80 tests
│   ├── test_sx_pipeline.py          ← 8 tests SX
│   ├── test_content_moderation.py   ← 10 tests
│   ├── test_authenticator_gate.py   ← 7 tests
│   └── ...
├── docker/
│   ├── wazuh-compose.yml            ← Wazuh stack (DEFERRED)
│   ├── netdata-compose.yml          ← Netdata (running, :19999)
│   ├── wazuh/
│   │   ├── wazuh-certs-tool.sh      ← Cert generator (đã chạy)
│   │   ├── config.yml               ← Cert config (127.0.0.1)
│   │   └── wazuh-certificates/      ← Certs đã generate (gitignored)
│   └── monitoring/
│       ├── .env.example             ← Template Wazuh credentials
│       └── .env                     ← Credentials thật (gitignored)
├── reports/arkon/
│   ├── approval-result.json         ← Human approve (scope=send_arkon_summary)
│   ├── approval-result-sx.json      ← Human approve SX
│   ├── queue/                       ← Retry queue (gitignored)
│   └── logs/                        ← Pipeline logs (gitignored)
├── .env.pipeline                    ← ARKON_PASSWORD + NETDATA_URL (gitignored)
└── .env.pipeline.example            ← Template

~/.config/systemd/user/
├── nurse-agents-pipeline.service    ← Systemd oneshot
└── nurse-agents-pipeline.timer      ← Hourly, Persistent=true

~/projects/arkon/
├── app/ai/embedding_catalog.py      ← ollama/nomic-embed-text-v2-moe (768d)
├── .claude/settings.json            ← mcpServers.arkon (project scope, CLI-generated)
├── .mcp.json                        ← MCP token (gitignored)
└── .gitignore                       ← bao gồm .mcp.json
```

---

## 6. Arkon Knowledge Base — trạng thái hiện tại

| Nguồn dữ liệu | Nội dung | Cập nhật |
|---|---|---|
| Monitoring summaries | Netdata metrics + GLPI tickets + alerts | Hourly (systemd timer) |
| File SX Index | 27 pages — 50 KH, 2828 files, 816 MB | On-demand (run_sx_pipeline.sh) |

**Query mẫu tại** `http://localhost:3119`:
- *"Khách hàng nào có nhiều file nhất?"*
- *"A Huyen có bao nhiêu file DXF?"*
- *"Tổng dung lượng file CNC của tất cả khách hàng?"*

---

## 7. Agent Layer — Phân công (V3)

| Tầng | Tool | Port | Nhiệm vụ |
|------|------|------|----------|
| Terminal | **Claude Code CLI** | — | High-quality task, architecture, security. Anthropic API trực tiếp |
| Interactive | **OpenCode** TUI/VSCode | — | Router, agent team, MCP, workflow. Human-in-the-loop |
| Autonomous | **SwarmClaw** | 3456 | Web UI, multi-agent song song, scheduling, delegation. Qua 9router/SW |
| On-demand | **Agent-Canvas** | 8000 | OpenHands web UI — coding agent tự động. Chạy khi cần |
| Advisory | **nous-hermes** | — | Read-only: giải thích, học lại, tóm tắt log, đề xuất skill |
| Router | **9router** | 20128 | Trung tâm — mọi AI request đều đi qua |

**Agents trong OpenCode (opencode.json):**
- `swarm-orchestrator` — model `9router/SW`, bash=ask, edit=deny — autonomous orchestration
- `senior-coder`, `reviewer`, `devops`, `db-analyst` — model `9router/Opencode`
- `architect`, `security-auditor` — model `9router/gh/gpt-4.1`
- `nous-hermes` — read/grep/glob only, mọi action đều deny
- `automation-planner`, `cost-optimizer`, `caveman`, `hermes-learning-coach`...

**Policy:** `nous-hermes` chỉ có quyền read/grep/glob. Toàn bộ bash/edit/MCP/task/memory đều bị deny.  
`swarm-orchestrator` có bash=ask, edit=deny — không tự sửa file, hỏi trước khi chạy lệnh.  
Chi tiết: [nous-hermes-policy.md](nous-hermes-policy.md)

**Binary install** (chạy thủ công 1 lần):
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

---

## 8. Nguyên tắc bất biến (không được thay đổi)

1. **Fail-closed:** mọi stage fail → dừng toàn bộ, không gửi gì
2. **Chỉ arkon-summary-reporter** được gửi lên Arkon — không direct push từ Wazuh/Netdata/GLPI
3. **Mọi payload** phải qua: sanitizer → validator → moderator → approval gate
4. **AI làm trong Ubuntu WSL2** — người dùng approve trên Windows; hoặc AI approve thay khi người dùng yêu cầu rõ ràng
5. **Không public:** Wazuh, Netdata, GLPI, OpenHands, One-API, Ollama, nurse-agents
6. **Wazuh DISABLED** cho đến khi đủ RAM + approval thủ công
7. **Không qua phase sau** nếu phase hiện tại chưa có verification-log PASS
8. **Không commit secret** — mọi .env đều gitignored
9. **nous-hermes read-only** — không bao giờ có quyền bash/edit/MCP; chỉ user mới kích hoạt action
10. **swarm-orchestrator** — bash=ask (hỏi trước), edit=deny; không tự sửa file production
11. **SwarmClaw** — route qua 9router/SW, không dùng local model (Ollama) cho hard task
12. **Không dùng Ollama** cho security/architecture/production — chỉ dùng cho embedding và task nhẹ
13. **AI làm trong Ubuntu, người dùng approve trên Windows** — approval-result.json tạo trên Windows; AI được phép tạo thay khi người dùng yêu cầu rõ ràng trong phiên làm việc

---

## Section 9 — V4 Agentic Layer (2026-06-10)

**Mục tiêu:** Biến OpenCode thành agentic assistant có state — agent biết project active, task dở, có thể checkpoint/resume qua restart. Additive only.

### Thay đổi

| Phase | Mô tả | Files |
|---|---|---|
| A — Project Context | Agent đọc state project khi bắt đầu session | `~/.config/opencode/project-context/{_active,nurse-agents,arkon}.md` + `instructions/project-context-loader.md` |
| B — Skills Coverage | +7 skills mới (bao gồm memory-ingest) | `skills/{session-resume,stack-health,pipeline-debug,arkon-query,approval-workflow,agent-handoff,memory-ingest}/SKILL.md` |
| C — Memory MCP | Enable memory MCP, thêm command consolidate | `opencode.json`: `mcp.memory.enabled=true` + command `memory-consolidate` |
| D — Task Tracker | Task files per project, cross-project global | `~/.config/opencode/tasks/{nurse-agents,arkon}/` + `global.md` |
| E — File Change | Backup protocol cho non-git files, undo command | `instructions/verify-workflow.md` append + command `undo-last-edit` |
| F — Checkpoint | Session save/resume qua restart | commands `session-checkpoint` + `session-resume` |

### Trạng thái sau V4

| Hạng mục | Giá trị |
|---|---|
| Commands | **26** (tăng từ 16) |
| Skills | **19 folders** (tăng từ 12) |
| Instructions | **5** (tăng từ 4) |
| Memory MCP | **enabled** |
| Project context | nurse-agents + arkon |
| Task tracker | nurse-agents + arkon + global |

---

## 10. V5 — Agentic Layer Completion (2026-06-10)

Parity với Claude Code. Additive only — không xóa/sửa gì của V4. 7 phases G–M.

| Phase | Mô tả | Files |
|---|---|---|
| G — Plan-first + Diff approval | Agent viết plan + hỏi trước khi sửa ≥2 files / config | `skills/plan-execute/SKILL.md` + `verify-workflow.md` (Diff approval) + command `plan-task` + `tasks/{nurse-agents,arkon}/plans/` |
| H — CLAUDE.md per-project | Auto-load project conventions | `~/projects/nurse-agents/CLAUDE.md` + `project-context-loader.md` rule 8 (arkon/CLAUDE.md đã có sẵn, giữ nguyên) |
| I — Post-edit auto-verify | Tự chạy test/lint/json-check sau khi edit | `skills/post-edit-verify/SKILL.md` + `verify-workflow.md` (Auto-verify after edit) |
| J — Git-aware context | Biết branch + uncommitted trước khi edit | `skills/git-context/SKILL.md` + `project-context-loader.md` rule 9 |
| K — Permission audit | Registry tier cho 18 agents (suy từ frontmatter thật) | `agents/PERMISSIONS.md` — agent files giữ nguyên |
| L — Context compaction | `/compact` command + cảnh báo session dài | command `compact` + `verify-workflow.md` (Long session) |
| M — Semantic code search | Ollama embeddings index codebase | `scripts/index-codebase.py` + `scripts/search-code.py` + command `search-code` |

### Trạng thái sau V5

| Hạng mục | Giá trị |
|---|---|
| Commands | **29** (26→29: +plan-task, +compact, +search-code) |
| Skills | **22 folders** (19→22: +plan-execute, +post-edit-verify, +git-context) |
| Instructions | 5 (project-context-loader có rule 8+9; verify-workflow có 3 section mới) |
| Agent permission registry | `agents/PERMISSIONS.md` — 18 agents, 4 tiers |
| Semantic search | code-index.db, 105 chunks, model nomic-embed-text-v2-moe |
| Verification-log | 7 entries V5 (G–M) đều PASS |

### Deviation đáng lưu (Phase M)
- Model embedding: `nomic-embed-text-v2-moe:latest` (đã có sẵn) thay vì `nomic-embed-text` trong handover.
- Chunk giới hạn 800 chars (model context nhỏ) + skip venv/cache dirs.

---

## Section 11 — V5.1 Reliability & Completeness (2026-06-10)

**Mục tiêu:** Lấp gap còn lại sau V5 — hướng đến "OpenCode ≥ Claude Code" về reliability.

### V5.1 Phases N–R

| Phase | Mô tả | Files tạo/sửa |
|---|---|---|
| N — /doctor | Unified diagnostics — bảng ✅/❌/⚠️ toàn hệ thống + verdict HEALTHY/DEGRADED/DOWN | `opencode.json` (+command `doctor`) |
| O — Closed-loop fix | Khi test FAIL → tự phân tích traceback → đề xuất fix → retry ≤3 lần → rollback suggestion | `skills/post-edit-verify/SKILL.md` (append) |
| P — wrap-up | Session-end protocol: checkpoint → memory → context → git status → summary | `opencode.json` (+command `wrap-up`) + `project-context-loader.md` (append rule 10) |
| Q — commit-suggest | Conventional Commits message + trigger re-index background sau commit .py | `opencode.json` (+command `commit-suggest`) |
| R — web-search | StackExchange API + PyPI — no API key, LIVE-VERIFIED | `scripts/web-search.py` + `skills/web-search/SKILL.md` + `opencode.json` (+command `search-web`) |

### Trạng thái sau V5.1

| Hạng mục | Giá trị |
|---|---|
| Commands | **33** (29→33: +doctor, +wrap-up, +commit-suggest, +search-web) |
| Skills | **23 folders** (22→23: +web-search) |
| Instructions | rule 10 "Session-end detection" thêm vào project-context-loader.md |
| post-edit-verify skill | +3 sections: Closed-loop Fix Protocol, Post-PASS actions, Web search trigger |
| Verification-log | 5 entries V5.1 (N–R) đều PASS — tổng 18 entries |
| web-search | Stack Overflow API + PyPI, no API key, LIVE-VERIFIED 2 queries |

### Deviation đáng lưu (Phase R)
- DuckDuckGo Lite trả challenge/CAPTCHA — switch sang StackExchange API (gzip, no key) + PyPI JSON API.
- Tốt hơn cho coding tasks: SO answers là nguồn chính của developer.

### Gap còn lại (V5.2 scope)
- Hooks (PreToolUse/PostToolUse): cần check OpenCode v1.16 API
- Parallel sub-agents nâng cao: cần SwarmClaw redesign
- Cost/token tracking: cần parse 9router log format
- Wazuh: blocked by RAM (cần ≥6GB free)

---

## Section 12 — V5.2 Observability & MCP Expansion (2026-06-10)

**Mục tiêu:** Token tracking, MCP đầy đủ hơn, auto re-index.

### V5.2 Phases S–U

| Phase | Mô tả | Files tạo/sửa |
|---|---|---|
| S — /cost-report | Token & cost từ 9router SQLite DB — today/week/all | `scripts/cost-report.py` + command `cost-report` |
| T — MCP expansion | Thêm filesystem + sequential-thinking (memory đã có V4) | `opencode.json` (+2 MCP servers enabled) |
| U — Auto re-index | Git post-commit hook tự re-index khi có .py commit | `scripts/install-git-hook.sh` (user chạy 1 lần) |

### Trạng thái sau V5.2

| Hạng mục | Giá trị |
|---|---|
| Commands | **34** (V5.2: +cost-report) |
| MCP servers enabled | filesystem, memory, sequential-thinking, gitnexus, windows-bridge, grounded-docs, context7 |
| Cost tracking | 9router DB → usageHistory/usageDaily, script ready |
| Auto re-index | Script install-git-hook.sh — user kích hoạt 1 lần |

### Để kích hoạt git hook (Phase U):
```bash
bash ~/.config/opencode/scripts/install-git-hook.sh
```

## Section 13 — V6 Plugin Architecture (2026-06-10/11)

### V6A — SDK Hook Daemon (DEPRECATED)
Daemon `~/.config/opencode/hooks/daemon.mjs` dùng `@opencode-ai/sdk` SSE qua `opencode serve :22000`. LIVE-VERIFIED (15 requests, 187k tokens) nhưng cần process riêng + reconnect loop. Đánh dấu DEPRECATED — giữ làm fallback.

### V6B — Official Plugin usage-tracker (ACTIVE)
| Thành phần | Chi tiết |
|---|---|
| Plugin | `~/.config/opencode/plugins/usage-tracker/index.js` — named export `UsageTracker` |
| Pattern | Dispatch map `HANDLERS` — mỗi event 1 handler riêng |
| Events | message.updated → usage.jsonl; session.idle → wrap-up-reminders.txt; file.watcher.updated (.py) → re-index; tool.execute.after → events.jsonl |
| Đăng ký | opencode.json key `plugin` (array) |
| Backward compat | Cùng log paths với daemon → cost-report.py không đổi |
| Ưu điểm | Không cần serve riêng, không reconnect loop, OpenCode inject context tự động |

## Section 14 — V6.3 Permission Gate "Nâng quyền có phanh" (2026-06-11)

**Mục tiêu:** Tự động hóa cao — agent tự thực thi lệnh an toàn; user chỉ duyệt lệnh nguy hiểm cuối.

### Thiết kế 3 lớp fail-closed
```
Lớp 1: opencode.json bash=ask GIỮ NGUYÊN  → plugin chết = mọi thứ vẫn hỏi
Lớp 2: plugin permission-gate             → safe=allow+audit / danger=ask / blocked=deny
Lớp 3: kill-switch ~/.config/opencode/SAFE_MODE → tồn tại = mọi thứ hỏi ngay
```

### Thành phần
| File | Vai trò |
|---|---|
| `plugins/permission-gate/index.js` | Hook `permission.ask` — phân loại + audit |
| `plugins/permission-gate/rules.json` | deny/ask/secret_guard patterns + whitelists — hot-reload, user chỉnh được |
| `instructions/auto-execution-policy.md` | Báo agents chế độ mới: batch không dừng, chỉ pause khi gate hỏi |
| Command `/permission-audit` | Xem 20 quyết định cuối + thống kê |
| Command `/safe-mode` | Toggle kill-switch |
| `hooks/logs/permission-audit.jsonl` | Audit trail mọi quyết định |

### On-Demand Read + Secret Guard
- **Read whitelist mặc định:** `~/projects`, `~/.config/opencode`, `/tmp` — ngoài đó (kể cả `/etc`, `/mnt/c`, `/mnt/d`) phải xin
- **Grant 1 lần/session/path:** user duyệt → đọc tiếp cùng path không hỏi lại; session đóng/restart → thu hồi
- **Secret Guard luôn bật:** `.env`, auth.json, credentials, keys, `.ssh/` — KHÔNG BAO GIỜ auto-allow kể cả trong path đã grant

### Trạng thái sau V6.3
| Hạng mục | Giá trị |
|---|---|
| Commands | **36** (+permission-audit, +safe-mode) |
| Plugins | **2** (usage-tracker, permission-gate) |
| Instructions | **7** (+language-policy, +auto-execution-policy) |
| T1 agents | Không đổi — vẫn deny (gate chỉ xử lý event "ask") |
| Live-verify | PENDING — checklist 7 mục trong verification-log V6.3 |

## Section 15 — V6.3.2 Hardening: Audit Rotation + Report (2026-06-12)

Bổ sung trên V6.3 (giữ nguyên mục tiêu thay claude.ai on-premise).

**B1 — Audit log rotation** (`plugins/permission-gate/index.js`):
- Hàm `audit()` gọi `rotateIfNeeded()` trước mỗi append.
- File `permission-audit.jsonl` > 2 MB → `renameSync` sang `.jsonl.1` (giữ 1 bản cũ, ghi đè .1 cũ).
- Lỗi rotation nuốt im (try/catch) — không bao giờ làm hỏng việc ghi audit.

**B2 — Command `/permission-audit` nâng cấp** (`opencode.json`):
- Stats theo cả `decision` lẫn `rule` (biết rule nào hay trigger).
- Cảnh báo file > 1.5 MB (sắp rotate ở 2 MB).
- Liệt kê file `.jsonl.1` nếu đã rotate.
- Giữ cảnh báo SAFE_MODE.

**Backups:** `index.js.bak-20260612-114219`, `opencode.json.bak-20260612-114219`.

**Verify:** `node --check index.js` → JS_OK; `json.load(opencode.json)` → JSON_OK.

**Còn lại (Phần C):** live-verify 7 mục gate (a–g) trong TUI sau restart — xem verification-log entry 2026-06-12 V6.3.2.
