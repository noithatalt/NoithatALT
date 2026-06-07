# OpenCode Build Summary — Tổng kết toàn bộ quá trình

**Cập nhật:** 2026-06-04 | **Tests:** 80/80 PASS | **Version:** V2.1.1 + SX + Nous Hermes Policy + Arkon MCP

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

### 3.1 — AI Stack tổng thể

```
┌─────────────────────────────────────────────────────────────────┐
│                        Windows Host                             │
│  Browser / VS Code / Terminal (Windows)                         │
└───────────────────────┬─────────────────────────────────────────┘
                        │ WSL2
┌───────────────────────▼─────────────────────────────────────────┐
│                    Ubuntu WSL2                                   │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐  │
│  │  OpenCode   │   │  Claude     │   │  Agent-Canvas        │  │
│  │  v1.15.13   │   │  Code CLI   │   │  npm :8000           │  │
│  └──────┬──────┘   └──────┬──────┘   └──────────┬───────────┘  │
│         └────────┬─────────┘                      │              │
│                  ▼                                 │              │
│  ┌───────────────────────────┐                    │              │
│  │  9router  :20128 (PM2)    │◄───────────────────┘              │
│  │  (OpenAI-compatible proxy)│                                   │
│  └──────────┬────────────────┘                                   │
│             ▼                                                     │
│   ┌─────────────────────────────────────────────┐               │
│   │  One-API  :3000  (model proxy backend)      │               │
│   └─────────┬───────────────────────────────────┘               │
│             │                                                     │
│   ┌─────────▼──────┐   ┌──────────────────────┐                 │
│   │  Anthropic API │   │  Ollama :11434        │                 │
│   │  (Claude 4.x)  │   │  9 models + embedding │                 │
│   └────────────────┘   └──────────────────────┘                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

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

### 4.8 — Wazuh (khi nâng RAM xong)

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

## 7. Agent Layer — Phân công 3 tầng (Nous Hermes Policy)

| Tầng | Tool | Nhiệm vụ |
|------|------|----------|
| Terminal | **Codex CLI** | Script, healthcheck, runtime/config test |
| Runtime | **OpenCode** | Router, agent team, MCP, workflow, permission |
| Advisory | **nous-hermes** | Giải thích, học lại, tóm tắt verification log đã lọc, đề xuất skill/checklist text |

**Policy:** `nous-hermes` chỉ có quyền read/grep/glob. Toàn bộ bash/edit/MCP/task/memory đều bị deny.  
Thao tác chỉ được kích hoạt khi người dùng chủ động chuyển sang agent phù hợp.  
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
4. **AI làm trong Ubuntu WSL2** — người dùng approve trên Windows
5. **Không public:** Wazuh, Netdata, GLPI, OpenHands, One-API, Ollama, nurse-agents
6. **Wazuh DISABLED** cho đến khi đủ RAM + approval thủ công
7. **Không qua phase sau** nếu phase hiện tại chưa có verification-log PASS
8. **Không commit secret** — mọi .env đều gitignored
9. **nous-hermes read-only** — không bao giờ có quyền bash/edit/MCP; chỉ user mới kích hoạt action
