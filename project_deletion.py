
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

from database import get_connection


# KNOVIA storage locations
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = (BASE_DIR / "data" / "uploads").resolve()
BACKUP_FOLDER = BASE_DIR / "backups"


def delete_project(project_id):

    project_id = int(project_id)

    # 1. Check that the project exists
    connection = get_connection()

    try:
        project = connection.execute(
            "SELECT project_name FROM projects WHERE id = ?",
            (project_id,)
        ).fetchone()

        if not project:
            return False, "Project not found."

        project_name = project[0]

        # 2. Collect uploaded file paths belonging to this project
        documents = connection.execute(
            "SELECT file_path FROM documents WHERE project_id = ?",
            (project_id,)
        ).fetchall()

        safe_files = []

        for document in documents:
            if not document[0]:
                continue

            file_path = Path(document[0]).resolve()

            # Only allow deletion inside KNOVIA's uploads folder
            if file_path.is_relative_to(UPLOAD_FOLDER):
                if file_path.is_file():
                    safe_files.append(file_path)

        # 3. Create a database backup
        BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        backup_path = (
            BACKUP_FOLDER /
            f"knovia_backup_{timestamp}.db"
        )

        backup_connection = sqlite3.connect(str(backup_path))

        try:
            connection.backup(backup_connection)
        finally:
            backup_connection.close()

        # 4. Delete SQLite records in a transaction
        connection.execute("BEGIN")

        connection.execute("""
            DELETE FROM leader_corrections
            WHERE recommendation_id IN (
                SELECT id FROM takeover_recommendations
                WHERE project_id = ?
            )
        """, (project_id,))

        connection.execute(
            "DELETE FROM takeover_recommendations WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM handover_reports WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM updates WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM decisions WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM tasks WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM documents WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM members WHERE project_id = ?",
            (project_id,)
        )

        connection.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    # 5. Remove this project's ChromaDB embeddings
    embedding_error = None

    try:
        from embedding_store import collection

        collection.delete(
            where={"project_id": project_id}
        )

    except Exception as error:
        embedding_error = str(error)

    # 6. Delete only the project's safe uploaded files
    file_errors = []

    for file_path in safe_files:
        try:
            file_path.unlink(missing_ok=True)
        except Exception as error:
            file_errors.append(str(error))

    # 7. Return the result
    message = (
        f"Project '{project_name}' (ID: {project_id}) "
        f"was deleted from SQLite. "
        f"Database backup: {backup_path}"
    )

    if embedding_error:
        message += (
            f" WARNING: ChromaDB cleanup failed: {embedding_error}"
        )

    if file_errors:
        message += (
            f" WARNING: Some uploaded files could not be deleted: "
            f"{file_errors}"
        )

    return True, message
