"""Repository primitives for loading/saving tabular data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


@dataclass(slots=True)
class SQLRepository:
    """Thin wrapper around SQLAlchemy for pandas workflows."""

    engine: Engine

    def fetch_df(self, query: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        """Run SQL query and return DataFrame."""
        return pd.read_sql_query(text(query), self.engine, params=params or {})

    def upsert_df(self, table: str, df: pd.DataFrame) -> None:
        """Append dataframe records to target table.

        For production workloads, use COPY + merge staging table. Here we keep a safe
        baseline implementation suitable for tests and small batches.
        """
        if df.empty:
            return
        df.to_sql(table, self.engine, if_exists="append", index=False, method="multi", chunksize=1000)
