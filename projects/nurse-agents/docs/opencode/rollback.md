# Rollback Guide

**Last updated:** 2026-06-04

Hướng dẫn rollback khi agent tạo code sai, config bị hỏng, hoặc cần undo thay đổi.

---

## Code Rollback

### Undo last commit (chưa push)
```bash
git reset --hard HEAD~1
```

### Undo last commit (giữ lại files để sửa)
```bash
git reset --soft HEAD~1
```

### Discard unstaged changes
```bash
git restore .
# hoặc file cụ thể:
git restore src/nurse_agents/api/diagnosis.py
```

### Discard staged changes
```bash
git restore --staged .
git restore .
```

### Go back to specific commit
```bash
git log --oneline -10        # tìm commit hash
git reset --hard <hash>      # rollback về đó
```

---

## OpenCode Config Rollback

### Nếu opencode.jsonc bị hỏng
```bash
# Restore từ backup gần nhất
ls ~/backups/opencode/
tar -xzf ~/backups/opencode/opencode_config_YYYYMMDD_HHMMSS.tar.gz -C ~/.config/

# Restart OpenCode để load config mới
```

### Nếu agent file bị sửa sai
```bash
# Xem diff
git diff ~/.config/opencode/agents/senior-coder.md  # nếu được track

# Hoặc restore từ backup
tar -xzf ~/backups/opencode/latest.tar.gz -C ~/.config/ opencode/agents/senior-coder.md
```

### Tạo backup ngay bây giờ (trước khi sửa)
```bash
bash ~/projects/nurse-agents/scripts/opencode/backup-opencode-config.sh
```

---

## Database Rollback

**nurse-agents** chưa có persistent database (dùng in-memory storage).
Khi thêm database, document migration rollback ở đây.

---

## Khi Nào Nên Rollback

| Tình huống | Hành động |
|---|---|
| Agent code không đúng yêu cầu | `git reset --hard HEAD~1` → prompt lại cụ thể hơn |
| Tests fail sau commit | `git reset --soft HEAD~1` → fix → recommit |
| Config bị hỏng | Restore từ backup |
| Branch bị mess | `git checkout main` → tạo branch mới từ main |
| Không chắc thay đổi gì | `git diff` trước khi rollback |

---

## Phòng Ngừa

1. **Commit thường xuyên** — sau mỗi bước hoàn thành, không phải cuối ngày
2. **Backup trước khi sửa config** — `backup-opencode-config.sh`
3. **Xem diff trước khi approve** agent changes — `y/n` cho từng thay đổi
4. **Branch per feature** — rollback 1 branch không ảnh hưởng main
5. **Test sau mỗi agent session** — `make test` ngay sau khi agent chạy xong

---

## Quick Reference

```bash
# Undo tất cả uncommitted changes
git restore . && git clean -fd

# Undo last commit (chưa push)  
git reset --hard HEAD~1

# Xem lịch sử để chọn điểm rollback
git log --oneline -20

# So sánh với main
git diff main...HEAD
```
