from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from swarm_powerbi_bot.services.sql_client import SqlClient

_SQL = "SELECT Id, Name FROM tbMasters WHERE ObjectId = @ObjectId"


class MasterResolver:
    def __init__(self, sql_client: SqlClient) -> None:
        self.sql_client = sql_client

    async def resolve(self, name: str, object_id: int) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = await self.sql_client.execute_query(
            _SQL, {"ObjectId": object_id}
        )
        threshold = 0.6 if len(name) <= 4 else 0.7
        candidates: list[dict[str, Any]] = []
        for row in rows:
            similarity = SequenceMatcher(
                None, name.lower(), str(row["Name"]).lower()
            ).ratio()
            if similarity >= threshold:
                candidates.append(
                    {
                        "id": int(row["Id"]),
                        "name": str(row["Name"]),
                        "similarity": round(similarity, 4),
                    }
                )
        candidates.sort(key=lambda c: c["similarity"], reverse=True)
        return candidates
