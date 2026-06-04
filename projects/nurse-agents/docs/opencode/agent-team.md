# Agent Team Reference

**Last updated:** 2026-06-04  
**Total agents:** 15

## Quick Selection Guide

```
Need to...                        Use agent
──────────────────────────────────────────────────
Design system before coding    →  architect
Write simple/small code        →  cheap-coder
Write complex/multi-file code  →  senior-coder
Review code or PR              →  reviewer
Search web / research          →  researcher
Database queries (read-only)   →  db-analyst
Infrastructure / deployment    →  devops
Audit security vulnerabilities →  security-auditor
Plan automation tasks          →  automation-planner
Optimize AI usage costs        →  cost-optimizer
Test in browser (Playwright)   →  browser-tester
Learn / understand code        →  hermes-learning-coach
```

## Full Agent Catalog

### architect
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: Starting a new feature, defining API contracts, choosing between design approaches
- **Output**: Architecture diagram, trade-offs, API contracts, recommended next agent
- **Do NOT use for**: Writing production code (delegate to senior-coder)

### cheap-coder
- **Model**: `9router/gh/gpt-4o-mini`
- **Use when**: Single-file changes, adding fields, fixing typos, simple CRUD
- **Output**: Working code + brief explanation
- **Cost**: Low — use first, escalate to senior-coder only if it fails

### senior-coder
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: Multi-file changes, complex logic, edge cases, sensitive refactors
- **Output**: Approach + impacted areas + risks + validation + residual concerns
- **Do NOT use for**: Simple single-file tasks (wastes cost)

### reviewer
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: PR review, pre-commit check, code quality audit
- **Output**: Findings ordered by severity, verdict (approve/request changes)

### researcher
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: Finding library docs, debugging unknown errors, researching best practices
- **Tools**: Web fetch, web search
- **Do NOT use for**: Questions answerable from the codebase (read files instead)

### db-analyst
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: Analyzing schema, writing read-only queries, understanding data relationships
- **Safety**: Read-only — never runs INSERT/UPDATE/DELETE

### devops
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: Docker, CI/CD, deployment scripts, infrastructure changes
- **Output**: Commands with explanation, rollback plan

### security-auditor
- **Model**: `9router/cx/gpt-5.3-codex`
- **Use when**: Before merging auth/API changes, after adding user inputs, pre-deploy check
- **Output**: Findings with severity (Critical/High/Medium/Low), clean areas, overall verdict
- **Do NOT use for**: Writing fixes (use senior-coder for that)

### automation-planner
- **Model**: `9router/gh/gpt-4o-mini`
- **Use when**: Breaking down large tasks into steps, planning automation workflows
- **Restriction**: Cannot run bash commands, read-only access
- **Output**: Ordered task list, agent assignments, dependencies

### cost-optimizer
- **Model**: `9router/gh/gpt-4o-mini`
- **Use when**: Monthly cost review, optimizing agent usage patterns
- **Output**: Usage breakdown, routing recommendations

### browser-tester
- **Model**: `9router/gh/gpt-4o-mini`
- **Use when**: Writing Playwright tests, automating web UI workflows
- **Requires**: `browser` MCP server enabled

### hermes-learning-coach
- **Model**: `9router/gh/gpt-4o-mini`
- **Use when**: Understanding unfamiliar code, onboarding, learning a concept deeply
- **Output**: Concept explanation + codebase example + mental model + next steps
- **Do NOT use for**: Writing production code

### planner
- **Model**: default
- **Use when**: General task planning (lightweight, no restrictions)

### coder
- **Model**: default
- **Use when**: General coding tasks not covered by cheap/senior-coder

### db-readonly
- **Model**: default
- **Use when**: Stricter read-only database access (more locked down than db-analyst)

## Escalation Ladder

```
cheap-coder → fails or uncertain → senior-coder
senior-coder → security concern found → security-auditor
automation-planner → needs implementation → senior-coder or cheap-coder
architect → design done → senior-coder for implementation
```

## Skills Available to All Agents

| Skill | Purpose |
|---|---|
| `workflow-plan` | Plan before coding |
| `review-plan` | Validate a plan |
| `code-review` | Review code changes |
| `security-review` | Security audit checklist |
| `mcp-debugging` | Fix MCP connection issues |
| `ai-learning` | Learning framework |
| `cost-optimization` | Reduce token usage |
| `feature-workflow` | End-to-end feature process |
| `bugfix-workflow` | End-to-end bug fix process |
| `security-audit` | Full security audit process |
| `role-audit` | Audit agent role coverage |
