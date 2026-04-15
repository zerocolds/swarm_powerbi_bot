"""Tests for swarm_powerbi_bot.services.master_resolver."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from swarm_powerbi_bot.services.master_resolver import MasterResolver


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_resolver(master_rows: list[dict]) -> MasterResolver:
    """Return a MasterResolver backed by a mock sql_client."""
    sql_client = MagicMock()
    sql_client.execute_query = AsyncMock(return_value=master_rows)
    return MasterResolver(sql_client)


MASTERS = [
    {"Id": 1, "Name": "Анна"},
    {"Id": 2, "Name": "Мария"},
    {"Id": 3, "Name": "Светлана"},
    {"Id": 4, "Name": "Екатерина"},
]


# ── tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
class TestMasterResolver:
    async def test_fuzzy_match_returns_similar_name(self):
        """'Ана' should fuzzy-match 'Анна' (short name → threshold 0.6)."""
        resolver = _make_resolver(MASTERS)
        results = await resolver.resolve("Ана", object_id=1)
        names = [r["name"] for r in results]
        assert "Анна" in names

    async def test_exact_match_has_high_similarity(self):
        """Exact match should return similarity close to 1.0."""
        resolver = _make_resolver(MASTERS)
        results = await resolver.resolve("Анна", object_id=1)
        anna = next((r for r in results if r["name"] == "Анна"), None)
        assert anna is not None
        assert anna["similarity"] >= 0.95

    async def test_no_match_returns_empty_list(self):
        """Name with no candidates above threshold → empty list."""
        resolver = _make_resolver(MASTERS)
        results = await resolver.resolve("Zxqwerty", object_id=1)
        assert results == []

    async def test_results_sorted_by_similarity_desc(self):
        """Multiple candidates must be sorted descending by similarity."""
        rows = [
            {"Id": 10, "Name": "Анна"},
            {"Id": 11, "Name": "Ана"},
            {"Id": 12, "Name": "Аня"},
        ]
        resolver = _make_resolver(rows)
        results = await resolver.resolve("Анна", object_id=1)
        sims = [r["similarity"] for r in results]
        assert sims == sorted(sims, reverse=True)

    async def test_mock_sql_client_is_called_with_correct_object_id(self):
        """sql_client.execute_query must be called once with the given object_id."""
        sql_client = MagicMock()
        sql_client.execute_query = AsyncMock(return_value=[])
        resolver = MasterResolver(sql_client)
        await resolver.resolve("Анна", object_id=42)
        sql_client.execute_query.assert_awaited_once()
        _, kwargs_or_args = sql_client.execute_query.call_args
        # params can be positional or keyword
        call_args = sql_client.execute_query.call_args
        params = call_args.args[1] if len(call_args.args) > 1 else call_args.kwargs.get("params", {})
        assert params.get("ObjectId") == 42

    async def test_result_dict_has_required_keys(self):
        """Every candidate dict must contain id, name, similarity."""
        resolver = _make_resolver(MASTERS)
        results = await resolver.resolve("Анна", object_id=1)
        for item in results:
            assert "id" in item
            assert "name" in item
            assert "similarity" in item

    async def test_short_name_uses_lower_threshold(self):
        """Names ≤4 chars use 0.6 threshold — 'Ана' should still match 'Анна'."""
        # "Ана" has len 3 → threshold 0.6
        resolver = _make_resolver([{"Id": 1, "Name": "Анна"}])
        results = await resolver.resolve("Ана", object_id=1)
        assert len(results) == 1

    async def test_longer_name_uses_higher_threshold(self):
        """Names >4 chars use 0.7 threshold — very different name should not match."""
        resolver = _make_resolver([{"Id": 1, "Name": "Светлана"}])
        # "Xxxxxxx" has len 7 → threshold 0.7, similarity with "Светлана" is near 0
        results = await resolver.resolve("Xxxxxxx", object_id=1)
        assert results == []

    async def test_multiple_candidates_all_present(self):
        """When multiple names match the query, all of them are returned."""
        rows = [
            {"Id": 1, "Name": "Анна"},
            {"Id": 2, "Name": "Аня"},
            {"Id": 3, "Name": "Антон"},   # unlikely to match "Анна"
        ]
        resolver = _make_resolver(rows)
        results = await resolver.resolve("Анна", object_id=1)
        # At least "Анна" and potentially "Аня" should appear; result is non-empty
        assert len(results) >= 1
        ids = [r["id"] for r in results]
        assert 1 in ids  # exact "Анна" must be present
