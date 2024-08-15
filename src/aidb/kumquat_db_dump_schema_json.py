# flake8: noqa: W503

import argparse
import json
from typing import Any

# Assuming this is your custom module for handling secrets
URL = "db://user:password@host:port/dbname"
from sqlalchemy import CheckConstraint, MetaData, create_engine, inspect


def kumquat_db_dump_table_schema_json(
    connection_string: str,
    tables: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Dump the schema of the specified tables in the database using a bulk operation."""
    engine = create_engine(connection_string)
    metadata = MetaData()
    metadata.reflect(engine, only=tables)

    if tables is not None:
        missing_tables = [table for table in tables if table not in metadata.tables]
        if missing_tables:
            raise ValueError(
                f"Requested table(s) not available in the database: {', '.join(missing_tables)}"
            )

    out: dict[str, dict[str, Any]] = {"tables": {}}

    for table_name, table in metadata.tables.items():
        table_info: dict[str, Any] = {
            "columns": [],
            "primary_key": [col.name for col in table.primary_key.columns],
            "indexes": [],
            "foreign_keys": [],
            "check_constraints": [],
            "table_comment": table.comment if hasattr(table, "comment") else None,
            "partitions": [],
        }

        # Add column information
        for column in table.columns:
            column_info = {
                "column_name": column.name,
                "data_type": str(column.type),
                "is_nullable": "YES" if column.nullable else "NO",
                "default": (
                    str(column.server_default.arg)  # type: ignore[attr-defined]
                    if column.server_default is not None
                    else (
                        str(column.default.arg)  # type: ignore[attr-defined]
                        if column.default is not None
                        else None
                    )
                ),
                "is_primary_key": column.primary_key,
                "comment": column.comment if hasattr(column, "comment") else None,
            }
            table_info["columns"].append(column_info)

        # Add index information
        for index in table.indexes:
            index_info = {
                "name": index.name,
                "unique": index.unique,
                "columns": [col.name for col in index.columns],
            }
            table_info["indexes"].append(index_info)

        # Add foreign key information
        for fk in table.foreign_keys:
            fk_info = {
                "column": fk.parent.name,
                "references": {"table": fk.column.table.name, "column": fk.column.name},
            }
            table_info["foreign_keys"].append(fk_info)

        # Add check constraints
        for constraint in table.constraints:
            if isinstance(constraint, CheckConstraint):
                check_info = {
                    "name": constraint.name,
                    "sqltext": str(constraint.sqltext),
                }
                table_info["check_constraints"].append(check_info)

        # Add partition information if available
        inspector = inspect(engine)
        if hasattr(inspector, "get_partitions"):
            partitions = inspector.get_partitions(table_name)
            if partitions:
                table_info["partitions"] = partitions

        out["tables"][table_name] = table_info

    return out


def create_args() -> argparse.Namespace:
    """Create an argument parser."""
    parser = argparse.ArgumentParser(
        description="Dump the schema of the specified tables or all tables in the database."
    )
    parser.add_argument(
        "connection_string",
        type=str,
        default=URL,
        help="Database connection string",
        required=True,
    )
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of table names to dump.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Dump schema for all tables in the database.",
    )
    return parser.parse_args()


def main() -> int:
    """Return 0 for success."""
    args = create_args()
    schema_str = ""
    try:
        if args.tables:
            table_names = [name.strip() for name in args.tables.split(",")]
            schema = kumquat_db_dump_table_schema_json(table_names)
            schema_str = json.dumps(schema, indent=2)

        else:
            user_input = input(
                "Enter the table names to dump (comma-separated) or '*' for all tables: "
            ).strip()
            if user_input == "":
                raise ValueError("No table names provided.")
            tables = user_input.split(",") if user_input != "*" else None
            schema = kumquat_db_dump_table_schema_json(tables)
            schema_str = json.dumps(schema, indent=2)
        print(schema_str)
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nAborted.")
        return 1


if __name__ == "__main__":
    main()
