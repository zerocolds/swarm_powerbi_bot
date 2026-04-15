---
description: "Запускает adversarial review через Gemini и Codex после прохождения speckit-ревью. Финальный гейт перед мержем."
---

You are running the Adversarial Review Gate — the final quality gate before merge.
This step runs AFTER all speckit reviews (review, staff-review, verify, verify-tasks) have PASSED.

## Prerequisites

Before running this command, confirm:
1. All speckit reviews have passed (review, staff-review, verify, verify-tasks)
2. You are on a feature branch (not main/master)
3. `gemini` and `codex` CLIs are available in PATH

If any prerequisite is not met, stop and inform the user.

## Execution Protocol

### Round Loop (max 3 rounds)

For each round (1 to 3):

**Step 1 — Run the adversarial review script**

```bash
.specify/scripts/adversarial-review.sh --round <N>
```

**Step 2 — Check exit code**

- **Exit 0** (both PASS): Report success and stop.
  ```
  ✅ ADVERSARIAL REVIEW PASSED
  Gemini: PASS
  Codex:  PASS
  Мерж разрешён. Запускайте /speckit.git.commit или создавайте PR.
  ```

- **Exit 1** (at least one FAIL): Continue to Step 3.

- **Exit 2** (environment error): Report the error and stop. Do not retry.

**Step 3 — Read findings and fix**

1. Read `.maqa/adversarial-findings.md` to understand which reviewer(s) failed and why.
2. Identify which findings are actionable code changes (not style preferences or false positives).
3. Spawn the **feature agent** (Sonnet) via the Agent tool to fix the actionable findings:

```
Agent({
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: "Fix the following adversarial review findings in the codebase. Only fix real issues — ignore style preferences and false positives. Findings:\n\n<paste findings here>\n\nAfter fixing, run: pytest -q && ruff check"
})
```

4. After fixes are applied, go to Step 1 with the next round number.

**Step 4 — Escalation (after round 3 FAIL)**

If round 3 still returns FAIL:

1. Read `.maqa/adversarial-findings.md` for the final findings.
2. Output:
   ```
   ⚠️ ЭСКАЛАЦИЯ НА ЧЕЛОВЕКА

   Adversarial review не пройден после 3 раундов исправлений.
   Полный лог замечаний: .maqa/adversarial-findings.md

   Требуется ручное решение:
   - Принять замечания и исправить вручную
   - Отклонить замечания с обоснованием
   - Переработать спецификацию
   ```
3. Do NOT proceed to merge. Do NOT run additional rounds. Stop.

## Important Rules

- Each retry runs ONLY the reviewer(s) that returned FAIL, not both.
  - If only Gemini failed: rerun only Gemini (the script reruns both, but only the failed verdict matters for the retry decision).
  - If only Codex failed: same logic.
- Never skip this gate. It is NON-NEGOTIABLE per the constitution (Principle V).
- Never auto-merge after escalation. Human decision is required.
- Preserve all round findings in `.maqa/adversarial-findings.md` for audit trail.
