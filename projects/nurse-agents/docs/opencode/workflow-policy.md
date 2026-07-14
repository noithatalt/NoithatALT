# Workflow Policy

**Last updated:** 2026-06-04

Quy tắc bắt buộc khi dùng OpenCode agents để code trong dự án nurse-agents.

---

## Quy tắc cốt lõi

### 1. Luôn tạo branch trước khi code
```bash
git checkout -b feature/my-feature    # tính năng mới
git checkout -b fix/bug-description   # bug fix
git checkout -b chore/task-name       # chores, docs, config
```
Không bao giờ commit thẳng vào `main`.

### 2. Plan trước khi implement (cho task phức tạp)
- Task chạm **3+ files** → dùng `/plan` hoặc `architect` agent trước
- Task < 3 files, rõ ràng → có thể code thẳng với `cheap-coder`

### 3. Test trước khi commit
```bash
make test        # bắt buộc pass
./scripts/fmt.sh # format code
```
Nếu test fail → fix trước, không commit.

### 4. Review trước khi push
```bash
git diff HEAD    # xem lại thay đổi
# hoặc dùng:
/code-review     # gọi reviewer agent
```

### 5. Commit message convention
```
feat: add X endpoint
fix: handle Y edge case
chore: update Z config
docs: add architecture guide
test: add coverage for W
refactor: simplify A logic
```

---

## Standard Feature Workflow

```
1. git checkout -b feature/xyz
2. /plan "implement xyz"          ← architect agent
3. /review-plan                   ← reviewer agent validates plan
4. /implement "step 1: ..."       ← senior-coder or cheap-coder
5. make test                      ← must pass
6. /code-review                   ← reviewer agent
7. ./scripts/fmt.sh               ← format
8. git add <specific files>
9. git commit -m "feat: ..."
10. git push -u origin feature/xyz
11. Create PR on GitHub
```

## Standard Bug Fix Workflow

```
1. git checkout -b fix/description
2. Write failing test first (proves bug exists)
3. /implement "fix: ..."          ← cheap-coder first
4. make test                      ← new test must pass, no regressions
5. /code-review                   ← verify fix is correct
6. git commit -m "fix: ..."
7. git push + PR
```

## Security-Sensitive Changes

For any change touching auth, user input, or external APIs:
```
After implementation:
  /security-check                 ← security-auditor agent
  → Fix all Critical and High findings before merging
  → Medium findings: fix before next release
```

---

## Agent Selection by Task Size

| Task | Agent | Command |
|---|---|---|
| Add a field to a model | cheap-coder | direct |
| New single-file function | cheap-coder | direct |
| New API endpoint | senior-coder | `/implement` |
| Multi-file refactor | senior-coder | `/plan` then `/implement` |
| New feature (3+ files) | architect → senior-coder | `/plan` → `/implement` |
| Bug with unclear root cause | researcher → senior-coder | investigate first |
| Security review | security-auditor | `/security-check` |

---

## What Agents Must NOT Do

- Commit or push to `main` directly
- Delete files without explicit user confirmation
- Modify `.env` or secrets files
- Run database migrations without review
- Install new dependencies without mentioning it

---

## PR Requirements

Before creating a PR, verify:
- [ ] All tests pass (`make test`)
- [ ] Code formatted (`./scripts/fmt.sh`)  
- [ ] No TODO/FIXME in new code
- [ ] No hardcoded secrets
- [ ] PR description explains what and why

PR title format: `feat: ...` / `fix: ...` / `chore: ...` (same as commit convention)
