# План реализации: Orchestrator fallback (#4)

**Ветка**: `feature/004-orchestrator-fallback-fix` | **Дата**: 2026-04-15

## Изменение

В `orchestrator.py`, блок строк ~139-147. Добавить третью ветку условия:

```python
has_multi_ok = any(r.status == "ok" for r in multi_results) if multi_results else False
multi_all_failed = bool(multi_results) and not has_multi_ok

if has_multi_ok:
    # multi OK — пропускаем legacy
    sql_insight = SQLInsight(rows=[], summary="skipped: multi_results available")
    pbi_insight = await self._run_pbi(question, plan, diagnostics)
elif multi_all_failed:
    # multi все failed — НЕ запускаем legacy SQL с catalog topic_id
    sql_insight = SQLInsight(rows=[], summary="multi_results all failed")
    pbi_insight = await self._run_pbi(question, plan, diagnostics)
    diagnostics["multi_all_failed"] = "true"
else:
    # legacy flow (нет multi_plan или нет multi_results)
    sql_task = ...
```

## Тесты

Файл: `tests/test_orchestrator.py` — тест что legacy SQL не вызывается при multi_all_failed.
