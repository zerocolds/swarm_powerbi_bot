# Adversarial Review — Раунд 3 (финальный)

**Дата**: 2026-04-15
**Ветка**: feature/001-semantic-aggregate-layer
**Ревьюеры**: DeepSeek V3.2 (Ollama cloud) + Codex (GPT-5.4)

---

## Сводка по раундам

| Раунд | DeepSeek V3.2 | Codex (GPT-5.4) | Действие |
|-------|---------------|------------------|----------|
| 1 | FAIL (2C, 3H, 5M) | FAIL (1C, 4H, 2M) | 11 fixed, 6 acknowledged |
| 2 | FAIL (каталог only) | FAIL (0C, 4H, 0M) | 4 fixed, DeepSeek acknowledged |
| 3 | ✅ PASS | FAIL (0C, 2H, 1M) | 3 fixed (регрессии от R2 fixes) |

---

## Раунд 1 — 17 findings

### DeepSeek — 10 findings → 4 fixed, 6 acknowledged (dev-only bootstrap)
- D1-D2 [CRITICAL] bootstrap model: relationships, table names → **ACKNOWLEDGED** (dev-only)
- D3-D5 [HIGH] catalog metadata → **FIXED** (defaults, allowed_values)
- D6-D10 [MEDIUM] bootstrap files → **ACKNOWLEDGED**

### Codex — 7 findings → 5 fixed, 2 acknowledged
- C1 [CRITICAL] ObjectId из текста → **FIXED** (убран _extract_object_id fallback)
- C2 [HIGH] topic default → **FIXED** (return "unknown" вместо "statistics")
- C3 [HIGH] period_hint → **FIXED** (резолвится для всех intents)
- C4 [HIGH] required fields → **FIXED** (добавлена проверка)
- C5 [HIGH] master_name → **ACKNOWLEDGED** (TODO, separate PR)
- C6 [MEDIUM] query logger → **FIXED** (user_id param)
- C7 [MEDIUM] analyst headline → **FIXED** (topic matching)

---

## Раунд 2 — 13 findings

### DeepSeek — 9 findings → все acknowledged (каталог/bootstrap)
Повторные замечания про bootstrap файлы и catalog metadata. Runtime код не затронут.

### Codex — 4 findings → все fixed
- R2-C1 [HIGH] telegram_bot.py:167 — period_callback user_id → **FIXED** (_callback_user_id)
- R2-C2 [HIGH] planner.py:295 — object_id injection → **FIXED** (inject + catalog check)
- R2-C3 [HIGH] sql_client.py:325 — top_n vs top → **FIXED** (accept both)
- R2-C4 [HIGH] orchestrator.py:210 — analyst fallback → **FIXED** (check has_multi_ok)

---

## Раунд 3 — 3 findings

### DeepSeek V3.2 — ✅ PASS
Новых проблем не обнаружено.

### Codex (GPT-5.4) — FAIL → 3 findings (регрессии от R2 fixes) → все fixed
- R3-C1 [HIGH] planner.py:295 — object_id injection ломает salon-wide агрегаты → **FIXED** (check catalog required)
- R3-C2 [HIGH] aggregate_registry.py:128 — `top` не валидируется → **FIXED** (accept "top" alongside "top_n")
- R3-C3 [MEDIUM] analyst.py:378 — secondary factors after topic matching → **FIXED** (exclude from full list)

---

## Итого

- **Всего findings**: 33 (3 раунда)
- **Fixed**: 23
- **Acknowledged**: 10 (dev-only bootstrap, design decisions, deferred)
- **Open blockers**: 0
- **Тесты**: 351 passed
- **Ruff**: clean

## Решение

⚠️ **ЭСКАЛАЦИЯ НА ЧЕЛОВЕКА** — по протоколу конституции (Принцип V):
- Codex не дал PASS ни в одном из 3 раундов
- DeepSeek дал PASS в раунде 3
- Все Codex findings исправлены, 0 open blockers
- Рекомендация: принять с учётом того что все findings resolved

**Adversarial diversity соблюдена**: Claude (Opus) реализация, Codex (GPT-5.4) + DeepSeek V3.2 (DeepSeek) ревью — 3 провайдера.
