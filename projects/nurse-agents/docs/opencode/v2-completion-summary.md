# OpenCode V2 — Tổng kết hoàn thành

**Ngày hoàn thành:** 2026-06-04  
**Tests:** 55/55 PASS  
**Verification log:** `docs/opencode/verification-log.md` — 6 entries PASS

---

## Những gì đã xây dựng

### Phase A — Policy & Guardrail docs (14 files)

| File | Mục đích |
|---|---|
| `current-state-audit.md` | Inventory đầy đủ: services, ports, agents, models |
| `network-exposure.md` | Public vs local-only, quy tắc expose |
| `hermes-memory-policy.md` | Không lưu raw log, token, secret |
| `caveman-role.md` | Gate chống over-engineering: KEEP/SIMPLIFY/KILL |
| `agent-primary-vs-subagent.md` | Phân loại 16 agents, đánh dấu legacy |
| `escalation-protocol.md` | Khi nào subagent dừng và leo thang |
| `command-agent-map.md` | 12 commands → owner agent |
| `arkon-reporting-policy.md` | Chỉ arkon-summary-reporter được gửi |
| `data-classification.md` | ALLOW / MASK / DENY table |
| `report-summary-schema.md` | JSON schema arkon-summary-v1 |
| `resource-budget.md` | RAM budget — không chạy Wazuh + Ollama nặng cùng lúc |
| `retention-policy.md` | Raw 30d, summaries 90d, verification-log không xóa |
| `failure-mode.md` | Fail-closed table |

### Phase B — Arkon pipeline

```
scripts/arkon/
  build_summary.py        # đọc Wazuh + Netdata + GLPI → summary.json
  redact_summary.py       # strip DENY fields, mask IPs → summary-redacted.json
  validate_summary.py     # schema check, exit 1 nếu fail
  send_summary_dry_run.py # dry-run, print payload, không gọi endpoint thật
  send_summary.py         # Phase E: POST thật, retry ×3, queue nếu fail
  load_glpi_tickets.py    # Phase F: GLPI tickets, PII stripped

tests/fixtures/monitoring/
  wazuh-alert-sample.json   # chứa secrets cố ý để test redaction
  netdata-sample.json
  glpi-ticket-sample.json

reports/arkon/
  summary.json              # output của build_summary
  summary-redacted.json     # output của redact_summary
  queue/                    # retry queue — KHÔNG commit lên git
```

### Phase C — Wazuh local lab

```
docker/wazuh-compose.yml              # single-node Wazuh 4.9.2
docker/monitoring/.env.example        # template credentials
scripts/monitoring/check-wazuh.sh     # health check từ WSL2
scripts/monitoring/check-wazuh-agent-windows.ps1  # check từ Windows
```

**Cách khởi động:**
```bash
cd ~/projects/nurse-agents/docker
cp monitoring/.env.example monitoring/.env
# Sửa passwords trong .env
docker compose -f wazuh-compose.yml --env-file monitoring/.env up -d
bash scripts/monitoring/check-wazuh.sh
```

### Phase D — Netdata local

```
docker/netdata-compose.yml         # port 127.0.0.1:19999 only
scripts/monitoring/check-netdata.sh
```

**Cách khởi động:**
```bash
docker compose -f docker/netdata-compose.yml up -d
bash scripts/monitoring/check-netdata.sh
```

### Phase E — Arkon real sender

```bash
# Set env vars (không bao giờ hardcode)
export ARKON_ENDPOINT=https://your-endpoint/
export ARKON_TOKEN=your-token

# Chạy pipeline đầy đủ
python3 scripts/arkon/build_summary.py
python3 scripts/arkon/redact_summary.py
python3 scripts/arkon/validate_summary.py
python3 scripts/arkon/send_summary.py

# Retry queue nếu có failed items
python3 scripts/arkon/send_summary.py --retry-queue
```

### Phase F — GLPI integration

```bash
export GLPI_URL=http://localhost/glpi
export GLPI_APP_TOKEN=...
export GLPI_USER_TOKEN=...
# build_summary.py tự động fetch tickets, fallback về fixture nếu không có env vars
```

---

## Security constraints (không được phá vỡ)

1. **Không public** Wazuh/Netdata/GLPI dashboard — tất cả bound 127.0.0.1
2. **Không gửi raw log** vào Arkon — `raw_logs_included` phải `false`
3. **Không gửi secret** — `secrets_included` phải `false`, redaction bắt buộc
4. **Fail-closed** — validate fail → không gửi gì
5. **Chỉ `arkon-summary-reporter`** được gửi lên Arkon
6. **Caveman gate** phải pass trước khi gửi Arkon thật lần đầu
7. **OpenHands** không sửa `~/.config/opencode` trực tiếp
8. **Hermes** không lưu raw log
9. **Không qua phase sau** nếu phase hiện tại chưa có verification-log PASS
10. **AI làm trong Ubuntu. Người dùng approve trên Windows.**

---

## V2.1 — Việc cần làm tiếp theo

### Ưu tiên cao
- [ ] **Wazuh agent Windows** — cài agent, trỏ về WSL2 127.0.0.1:1515, chạy `.ps1` check
- [ ] **Pipeline end-to-end với Wazuh thật** — khởi động compose, set env, chạy build_summary
- [ ] **Netdata chart names WSL2** — verify `disk_space./` hay `disk_space._` trong môi trường thật

### Ưu tiên trung bình
- [ ] **Arkon real endpoint** — cần user cung cấp ARKON_ENDPOINT + ARKON_TOKEN
- [ ] **Scheduled pipeline** — `scripts/arkon/run_pipeline.sh` + systemd timer hoặc cron

### Ưu tiên thấp
- [ ] **GLPI local Docker** — tạo `docker/glpi-compose.yml` nếu cần test GLPI thật
- [ ] **Wazuh alerts → nhiều item** — hiện fixture chỉ có 1 alert; test với nhiều alerts

### Lưu ý kỹ thuật
- `pyproject.toml` `pythonpath = ["src", "scripts/arkon"]` — nếu thêm script dir mới phải update
- `reports/arkon/queue/` — thêm vào `.gitignore`
- Wazuh 4.9.2 — không tự upgrade
- RAM: Wazuh (~6-10GB) + Ollama nặng + OpenHands = quá tải. Chạy từng cái một.
