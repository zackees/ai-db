import argparse
import atexit
import json
import os
import shutil
import subprocess
import sys
import time
from tempfile import NamedTemporaryFile

from aidb.db_dump_schema_json import db_dump_table_schema_json

AI_PROMPT = """
You are an expert SQL engineer.
Ingest the following db schema in json format and use this for your answers.
If someone asks for a year and month, see if there is a YRMO column in the table
and if so, attempt to use the YRMO column in your query, because that is indexed.

Do not try and give multiple queries. If possible, generate just one query for the user request.

If the query involves counting the number of rows AND yrmo exists in the table,
ask the user if they would like to group by yrmo with a [y/n] response. Then based on that
response generating the SQL query.
"""


def create_args() -> argparse.Namespace:
    """Create an argument parser."""
    parser = argparse.ArgumentParser(
        description="Dump the schema of the specified tables or all tables in the database."
    )
    parser.add_argument(
        "connection_string", type=str, help="Database connection string"
    )
    return parser.parse_args()


def main() -> int:
    """Return 0 for success."""
    args = create_args()
    connection_string = args.connection_string
    askai_exists = shutil.which("askai") is not None
    if not askai_exists:
        print('askai is not installed, install it with "pip install zcmds"')
        return 1
    try:
        print("This tool will generate SQL queries for you to run on the database.")
        table_names_str = input(
            "\nEnter the table names you want to ask\n"
            "You can list each table (comma seperated) or use '*' to ask about all the tables in the db:\n>>> "
        )
        table_names = table_names_str.strip().split(",")
        try:
            schema = db_dump_table_schema_json(
                connection_string=connection_string, tables=table_names
            )
            simple_schema_str = ""
            table_schema = schema["tables"]
            for table_name, table_info in table_schema.items():
                column_schema = table_info["columns"]
                simple_schema_str += f"{table_name}\n"
                for column in column_schema:
                    name = column["column_name"]
                    data_type = column["data_type"]
                    simple_schema_str += f"  {name}: {data_type}\n"
                simple_schema_str += "\n"
            print(f"\nSchema:\n{simple_schema_str}")
            schema_str = json.dumps(schema, indent=2)
        except ValueError as e:
            print(f"Error: {e}")
            return 1
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return 1

        with NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as temp_file:
            temp_file.write(f"AI Prompt: {AI_PROMPT}\n\n")
            temp_file.write(schema_str)
            temp_file_path = temp_file.name

        # Register the cleanup function to be called at exit
        atexit.register(lambda: os.unlink(temp_file_path))
        print(
            "\nWith the following prompt describe in natural language what you want to query."
        )
        process = subprocess.Popen(
            ["askai", "--assistant-prompt-file", temp_file_path, "--check"]
        )
        try:
            process.wait()
        except KeyboardInterrupt:
            print("Process aborted by user.")
            process.terminate()
            process.wait()
            time.sleep(1)
            return 1

        if process.returncode != 0:
            print("An error occurred while running askai.")
            return 1

        return 0
    except KeyboardInterrupt:
        print("Program aborted by user.")
        return 1
    except FileNotFoundError as e:
        print(f"Error: File not found. {e}")
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied. {e}")
        return 1
    except subprocess.SubprocessError as e:
        print(f"Error in subprocess execution: {e}")
        return 1
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
