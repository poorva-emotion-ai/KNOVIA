import sqlite3

DB_NAME = "knovia.db"


# Connect to database
def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# Create database tables
def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Members table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            name TEXT NOT NULL,
            member_name TEXT,
            role TEXT,
            email TEXT,
            skills TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            member_id INTEGER,
            task_name TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            description TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        )
    """)

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            file_name TEXT NOT NULL,
            file_path TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Updates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            member_id INTEGER,
            update_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        )
    """)

    # Decisions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            decision_title TEXT NOT NULL,
            decision_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # Takeover Recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS takeover_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            task_id INTEGER NOT NULL,
            departing_member_id INTEGER NOT NULL,
            recommended_member_id INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (departing_member_id) REFERENCES members(id),
            FOREIGN KEY (recommended_member_id) REFERENCES members(id)
        )
    """)
    # Leader Corrections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leader_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recommendation_id INTEGER NOT NULL,
            corrected_member_id INTEGER NOT NULL,
            correction_note TEXT,
            corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (recommendation_id)
                REFERENCES takeover_recommendations(id),

            FOREIGN KEY (corrected_member_id)
                REFERENCES members(id)
        )
    """)

        # Handover Reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS handover_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            departing_member_id INTEGER NOT NULL,
            report_content TEXT NOT NULL,
            incoming_member_guide TEXT,
            approval_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,

            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (departing_member_id) REFERENCES members(id)
        )
    """)

    connection.commit()
    connection.close()

    print("KNOVIA Database Created Successfully!")