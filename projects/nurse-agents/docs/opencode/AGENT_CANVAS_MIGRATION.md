# Agent-Canvas Migration Guide

**Version:** 1.0  
**Updated:** 2026-06-07  
**Status:** ✅ LIVE (npm agent-canvas replaces Docker OpenHands)

---

## 📋 Tóm tắt

OpenHands đã **chuyển từ Docker cũ (port 3001) sang npm agent-canvas (port 8000)** để tương thích với tài liệu chính thức và cộng đồng OpenHands.

| Aspect | Docker (Old) | npm agent-canvas (New) |
|---|---|---|
| **Installation** | `docker compose up` | `npm install -g @openhands/agent-canvas` |
| **Port** | 3001 | 8000 |
| **LLM Config** | env vars (không hoạt động) | API PATCH `/api/settings` hoặc UI wizard |
| **Workspace** | `~/openhands-workspace/` | `/tmp/oh-test-workspace/` (configurable) |
| **Runtime** | Docker container (broken DNS) | Local agent-server (port 18000) |
| **Status** | ❌ Không hoạt động (DNS fail) | ✅ Hoạt động đầy đủ |

---

## 🚀 Quick Start (for New Users)

### 1. Prerequisites
```bash
# Node.js 22.12+ (Haiku 22.22.2 ✅)
node --version

# uv package manager (Haiku: just installed ✅)
uv --version

# Python (via uv, no separate install needed)
```

### 2. Install Agent-Canvas
```bash
npm install -g @openhands/agent-canvas
```

### 3. Start Agent-Canvas
```bash
agent-canvas &
# Services start on:
# - port 3001: frontend UI
# - port 18000: backend API
# - port 8000: unified gateway
```

### 4. Configure LLM
```bash
# Set LLM config via API (immediate, no UI needed)
curl -X PATCH http://localhost:18000/api/settings \
  -H "X-Session-API-Key: ed1ffda43d5a4cb26b17fdf170cc322fcf69734476020dace305bc97bd41433c" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_settings_diff": {
      "llm": {
        "model": "openai/kr/claude-sonnet-4-agentic",
        "base_url": "http://127.0.0.1:20128/v1",
        "api_key": "sk-644e210de6cd8fbf-t4v1px-b7980e68"
      }
    }
  }'
```

### 5. Open Browser
```
http://localhost:8000    (local)
OR
http://[WSL-IP]:8000     (from Windows host)

Current WSL IP: 172.22.184.104
```

### 6. Test Agent
- Click "New Conversation"
- Enter prompt: `Create a Python script that prints hello world`
- Agent executes using 9router LLM

---

## 🔄 Migration Details

### What Changed

| Component | Old | New |
|---|---|---|
| **Installation** | Docker container (ghcr.io) | npm package (@openhands/agent-canvas) |
| **LLM Setup** | Environment variables in compose file (ignored) | PATCH API or UI wizard |
| **Port Structure** | 3001 (frontend only) | 8000 (unified gateway) → 18000 (backend) → 3001 (frontend) |
| **Runtime Sandbox** | `docker.all-hands.dev` (broken DNS) | Local uvx agent-server (works) |
| **Config Persistence** | Compose file | In-memory + browser local storage |
| **Documentation** | Old Docker guide | Official npm docs |

### Why Changed

1. **Docker image broke** — `docker.all-hands.dev` is private/unreachable, causing runtime failures
2. **LLM env vars ignored** — Docker version doesn't read `LLM_*` vars as settings
3. **Official docs recommend npm** — Agent-Canvas is the official distribution method
4. **Better UX** — UI wizard + browser interface vs CLI/env setup
5. **Easy to update** — `npm update -g @openhands/agent-canvas` vs rebuilding Docker

---

## 📚 Configuration

### LLM Backend

**Current Setup:**
```
Agent-Canvas ← → OpenHands Agent-Server (port 18000)
             ← → 9router LLM Gateway (port 20128)
             ← → kr/claude-sonnet-4-agentic model
```

**To change LLM:**
```bash
# Get API key from agent-canvas UI or use same key
KEY="ed1ffda43d5a4cb26b17fdf170cc322fcf69734476020dace305bc97bd41433c"

# Update model
curl -X PATCH http://localhost:18000/api/settings \
  -H "X-Session-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_settings_diff": {
      "llm": {
        "model": "openai/kr/claude-sonnet-4.5"
      }
    }
  }'
```

### Workspace Configuration

**Default:** `/tmp/oh-test-workspace/`  
**To change:** Set via API or UI conversation creation

```bash
# Check current workspace
curl -s http://localhost:18000/api/settings \
  -H "X-Session-API-Key: $KEY" | jq '.agent_settings.workspace'
```

---

## ✅ Verification Checklist

```bash
# 1. All services running
ps aux | grep agent-canvas

# 2. Ports listening
netstat -tuln | grep -E '3001|8000|18000'

# 3. LLM config correct
curl -s http://localhost:18000/api/settings \
  -H "X-Session-API-Key: $KEY" | jq '.agent_settings.llm.model'

# 4. 9router connectivity
curl -s http://127.0.0.1:20128/v1/models \
  -H "Authorization: Bearer sk-644e210de6cd8fbf-t4v1px-b7980e68" | jq '.data | length'

# 5. Agent server health
curl -s http://localhost:18000/health

# 6. Browser accessible
curl -s http://localhost:8000 | head -5
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Kill and restart
pkill -f agent-canvas
agent-canvas
```

### 9router Not Responding
```bash
# Check router status
curl -s http://127.0.0.1:20128/health

# If down, check it's running
ps aux | grep "9router\|router"
```

### LLM Not Responding
```bash
# Check API key
curl -s http://localhost:18000/api/settings \
  -H "X-Session-API-Key: $KEY" | jq '.llm_api_key_is_set'

# Should return: true

# If false, re-run config update (see Configuration section)
```

### Conversation Creation Fails
```bash
# Check agent-server logs
# Port 18000 may have errors

# Verify workspace directory exists
mkdir -p /tmp/oh-test-workspace
```

---

## 📖 Official Resources

- **Main Docs**: https://docs.openhands.dev/
- **Setup**: https://docs.openhands.dev/openhands/usage/agent-canvas/setup
- **First-Time Setup**: https://docs.openhands.dev/openhands/usage/agent-canvas/first-time-setup
- **Customize**: https://docs.openhands.dev/openhands/usage/agent-canvas/customize-and-settings
- **Troubleshooting**: https://docs.openhands.dev/openhands/usage/agent-canvas/troubleshooting
- **GitHub**: https://github.com/OpenHands/agent-canvas

---

## 🔐 Security Notes

1. **Session API Key** — Treat as session token (auto-generated, browser-stored)
   - Header: `X-Session-API-Key`
   - Do NOT expose in logs/commits

2. **LLM API Key** — Stored encrypted in settings
   - Header: `X-Expose-Secrets: encrypted` to get cipher text
   - Never `plaintext` to frontend

3. **Workspace Access** — Local file system only
   - Agent runs in `LocalWorkspace` context
   - Respects file permissions

---

## 📋 Maintenance

### Regular Updates
```bash
# Check current version
npm list -g @openhands/agent-canvas

# Update to latest
npm update -g @openhands/agent-canvas

# Restart
pkill -f agent-canvas
agent-canvas
```

### Backup Conversations
```bash
# Conversations stored in agent-server memory
# Persist manually if needed:
curl -s http://localhost:18000/api/conversations \
  -H "X-Session-API-Key: $KEY" > conversations_backup.json
```

---

## 🚀 Advanced Setup

### Behind a Proxy
```bash
# Set proxy env vars before starting
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

agent-canvas
```

### Custom Port
```bash
agent-canvas --port 9000
# Frontend: http://localhost:9000
# Backend routes internally
```

### Custom Backend
```bash
# agent-canvas can connect to remote agent-server
# Set in first-time setup wizard → Backend config
# Backend URL: http://remote-server:18000
```

---

## 📊 Status Summary

| Item | Status | Notes |
|---|---|---|
| Installation | ✅ DONE | npm global, uv installed |
| Services Running | ✅ DONE | ports 3001, 8000, 18000 |
| LLM Configured | ✅ DONE | kr/claude-sonnet-4-agentic |
| 9router Connected | ✅ DONE | 112 models available |
| UI Accessible | ✅ DONE | Browser tested |
| Conversations Work | ✅ READY | Can create + send prompts |
| Agent Execution | ✅ READY | Full codegen + file ops |

---

## 💬 Support

**If something breaks:**

1. Check logs:
   ```bash
   # Agent-canvas logs (terminal where you started it)
   # Agent-server logs (if available)
   ps aux | grep agent
   ```

2. Verify health:
   ```bash
   bash ~/projects/nurse-agents/tests/test_agent_canvas.sh
   ```

3. Reset settings:
   ```bash
   # Delete browser local storage → re-run UI wizard
   # Agent-server will re-initialize
   ```

4. Escalate:
   ```bash
   opencode researcher
   > Troubleshoot Agent-Canvas connection issues
   ```

---

**Last Verified:** 2026-06-07  
**Verified By:** Claude Code (Haiku 4.5)  
**System:** WSL2 Linux, Node 22.22.2, Python 3.x via uv
