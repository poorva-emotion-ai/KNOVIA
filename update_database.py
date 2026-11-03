
import sqlite3

DB_NAME = "knovia.db"


def add_column_if_missing(cursor, table_name, column_name, definition):

    cursor.execute(f"PRAGMA table_info({table_name})")

    columns = [column[1] for column in cursor.fetchall()]

    if column_name not in columns:

        cursor.execute(
            f"ALTER TABLE {table_name} "
            f"ADD COLUMN {column_name} {definition}"
        )

        print(f"Added column: {table_name}.{column_name}")

    else:
        print(f"Column already exists: {table_name}.{column_name}")


def update_database():

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    try:

        # ==================================
        # UPDATE PROJECTS TABLE
        # ==================================

        add_column_if_missing(
            cursor, "projects", "domain", "TEXT"
        )

        add_column_if_missing(
            cursor, "projects", "start_date", "TEXT"
        )

        add_column_if_missing(
            cursor, "projects", "status", "TEXT DEFAULT 'Active'"
        )

        # ==================================
        # UPDATE MEMBERS TABLE
        # ==================================

        add_column_if_missing(
            cursor, "members", "project_id", "INTEGER"
        )

        add_column_if_missing(
            cursor, "members", "member_name", "TEXT"
        )

        add_column_if_missing(
            cursor, "members", "role", "TEXT"
        )

        add_column_if_missing(
            cursor, "members", "email", "TEXT"
        )

        add_column_if_missing(
            cursor, "members", "skills", "TEXT"
        )

        add_column_if_missing(
            cursor, "members", "current_workload",
            "TEXT DEFAULT 'unknown'"
        )

        # ==================================
        # UPDATE TASKS TABLE
        # ==================================

        add_column_if_missing(
            cursor, "tasks", "required_skills", "TEXT"
        )

        connection.commit()

        print("\nKNOVIA Database Updated Successfully!")

    except Exception:

        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    update_database()
