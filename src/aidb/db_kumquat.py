"""
DB Access functions.
"""

from typing import Any, Sequence

import sqlalchemy
from kumquat.secrets import secrets
from sqlalchemy import Row, text
from sqlalchemy.engine import Result


# Example SQL query
#    sql = f"""
#    SELECT youtube.id, youtube.url, youtube.html, youtube.next_url, youtube.datetime, youtube.yrmo
#    FROM youtube
#    LEFT JOIN youtube_details ON youtube.id = youtube_details.youtube_id
#    WHERE youtube_details.youtube_id IS NULL
#    LIMIT {limit};
#    """
def query_kumquat(
    sql: str, db_url: str | None = None, timeout: int | None = 5 * 60
) -> Sequence[Row[Any]]:
    """Query the kumquat database."""
    # xTODO: make query_kumquat use params: dict[str, Any] = {} instead of string interpolation
    db_url = db_url or secrets().db_kumquat_url_prod_r
    engine = sqlalchemy.create_engine(
        url=db_url, connect_args={"connect_timeout": timeout}
    )
    with engine.connect() as conn:
        sql_text = text(sql)
        result = conn.execute(sql_text)
        return result.fetchall()


# Like query_kumquat, but also allows updates.
# def update_kumquat(sql: str, db_url: str | None = None) -> None:
# add a return value
def update_kumquat(
    sql: str,
    params: dict[str, Any] | list[dict],
    db_url: str | None = None,
    timeout: int | None = 5 * 60,
) -> Result:
    """Update the kumquat database."""
    db_url = db_url or secrets().db_kumquat_url_prod_rw
    conn: sqlalchemy.engine.Connection | None
    try:
        engine = sqlalchemy.create_engine(
            url=db_url, connect_args={"connect_timeout": timeout}
        )
        with engine.connect() as conn:
            sql_text = text(sql)
            result = conn.execute(sql_text, params)  # Pass parameters to execute
            conn.commit()
            return result
    except Exception:
        # Handle rollback in case of error
        if conn:
            conn.rollback()
        # Log or handle the error as necessary
        raise
