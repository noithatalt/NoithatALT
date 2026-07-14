# External Send Control Policy

**Version:** external-send-v1
**Muc tieu:** Kiem soat moi duong di cua du lieu tu he thong local ra ngoai.

## Nguyen tac

Khong co gi tu he thong local duoc phep di ra ngoai ma khong qua:
  sanitizer -> validator -> content-moderator -> approval-gate

## Cac duong outbound hien tai

| Duong            | Dich          | Kiem soat              | Ghi chu                    |
|------------------|---------------|------------------------|----------------------------|
| cloudflared      | Internet      | Canonical WSL config   | Chi n8n + claude theo chu dich |
| Arkon summary    | Arkon API     | Full 4-buoc pipeline   | Bat buoc                   |
| Git push         | GitHub        | Manual approval        | Khong auto-push            |
| Docker pull      | Docker Hub    | Build time only        | Read-only                  |
| npm/pip install  | Registry      | Build time only        | Khong runtime download     |

## Cam tuyet doi

- Wazuh khong gui truc tiep Arkon
- Netdata khong gui truc tiep Arkon
- GLPI khong gui truc tiep Arkon
- Hermes khong gui raw log ra ngoai
- OpenHands khong push code khong co approval
- Khong expose Wazuh/Netdata/GLPI dashboard qua cloudflare

## Dashboard binding policy

| Dashboard | Bind             | cloudflare | Ghi chu          |
|-----------|------------------|------------|------------------|
| Wazuh     | 127.0.0.1:443    | KHONG      | Local lab only   |
| Netdata   | 127.0.0.1:19999  | KHONG      | Local only       |
| GLPI      | 127.0.0.1:8080   | KHONG      | De sau           |
| Agent-Canvas | 127.0.0.1:8000   | KHONG      | AI coding agent  |
| One-API   | 127.0.0.1:3000   | KHONG      | Model proxy      |

## Kiem tra sau moi thay doi cloudflared

```bash
bash scripts/opencode/mcp-healthcheck.sh
bash scripts/monitoring/check-wazuh.sh
```

Xac nhan khong co port Wazuh/Netdata nao bind 0.0.0.0 public.
