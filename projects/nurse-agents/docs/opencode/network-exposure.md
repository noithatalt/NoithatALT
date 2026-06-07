# Network Exposure Policy

## Public (qua Cloudflare tunnel — có chủ đích)

| Hostname | Backend | Ghi chú |
|---|---|---|
| `n8n.noithatalt.io.vn` | `localhost:5678` | Cần auth |
| `claude.noithatalt.io.vn` | `localhost:20128` | 9router gateway |

**Chỉ những gì được liệt kê ở trên mới được public.**

## Services và bind address

| Service | Port | Bind | Ghi chú |
|---|---:|---|---|
| Agent-Canvas | 8000 | 127.0.0.1 | npm — localhost only |
| One-API | 3000 | 127.0.0.1 | Model proxy — chứa API keys |
| 9router | 20128 | 0.0.0.0 | Gateway chính |
| Ollama | 11434 | 127.0.0.1 | Model inference local |
| nurse-agents | 8000 | localhost | Internal API |
| Wazuh Manager | 1514, 55000 | 127.0.0.1 | Security data nhạy cảm |
| Wazuh Dashboard | 443 | 127.0.0.1 | KHÔNG bao giờ public |
| Wazuh Indexer | 9200 | 127.0.0.1 | Raw security events |
| Netdata | 19999 | 127.0.0.1 | System metrics |
| GLPI | TBD | 127.0.0.1 | Ticket data nội bộ |
| n8n | 5678 | localhost | Cần auth trước khi public |

## Quy tắc bất biến

- Không thêm port mới vào cloudflare tunnel mà không có approval.
- Monitoring dashboard (Wazuh, Netdata, GLPI) không bao giờ public.
- API keys và secrets không đi qua tunnel.
- Mọi data ra ngoài phải qua: sanitizer → validator → moderator → approval gate.
- Agent-Canvas (port 8000) localhost only, không expose qua cloudflare.
