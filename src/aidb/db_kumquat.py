"""
DB Access functions.
"""

from typing import Any, Sequence

import sqlalchemy
from sqlalchemy import Row, text


# Example SQL query
#    sql = f"""
#    SELECT youtube.id, youtube.url, youtube.html, youtube.next_url, youtube.datetime, youtube.yrmo
#    FROM youtube
#    LEFT JOIN youtube_details ON youtube.id = youtube_details.youtube_id
#    WHERE youtube_details.youtube_id IS NULL
#    LIMIT {limit};
#    """
def query_kumquat(
    db_url: str, sql: str, timeout: int | None = 5 * 60
) -> Sequence[Row[Any]]:
    """Query the kumquat database."""
    # xTODO: make query_kumquat use params: dict[str, Any] = {} instead of string interpolation
    engine = sqlalchemy.create_engine(
        url=db_url, connect_args={"connect_timeout": timeout}
    )
    with engine.connect() as conn:
        sql_text = text(sql)
        result = conn.execute(sql_text)
        return result.fetchall()
