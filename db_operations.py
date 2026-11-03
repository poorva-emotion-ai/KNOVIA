from database import get_connection


# ==================================
# PROJECT MANAGEMENT
# ==================================

def create_project(
    project_name,
    description,
    domain=None,
    start_date=None,
    status="Active"
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO projects (
            project_name,
            description,
            domain,
            start_date,
            status
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        project_name,
        description,
        domain,
        start_date,
        status
    ))

    project_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return project_id


def get_all_projects():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM projects")

    projects = cursor.fetchall()

    connection.close()

    return projects

def get_projects_for_dashboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            project_name,
            description,
            domain,
            start_date,
            status,
            created_at
        FROM projects
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    projects = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "domain": row[3],
            "start_date": row[4],
            "status": row[5],
            "created_at": row[6]
        }
        for row in rows
    ]

    connection.close()

    return projects


# ==================================
# TEAM MEMBER MANAGEMENT
# ==================================

def add_member(
    project_id,
    member_name,
    role="Team Member",
    email=None,
    skills=None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO members (
            project_id,
            name,
            member_name,
            role,
            email,
            skills
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        member_name,
        member_name,
        role,
        email,
        skills
    ))

    member_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return member_id


def get_project_members(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM members
        WHERE project_id = ?
    """, (project_id,))

    members = cursor.fetchall()

    connection.close()

    return members


# ==================================
# TASK MANAGEMENT
# ==================================

def add_task(project_id, member_id, task_name, status, description,
             required_skills=None):

    if isinstance(required_skills, (list, tuple, set)):
        required_skills = ", ".join(
            str(skill).strip()
            for skill in required_skills
            if str(skill).strip()
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (project_id, member_id, task_name, status, description, required_skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        member_id,
        task_name,
        status,
        description,
        required_skills
    ))

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return task_id


def get_project_tasks(project_id):
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            tasks.id,
            tasks.project_id,
            tasks.member_id,
            members.member_name,
            tasks.task_name,
            tasks.status,
            tasks.description,
            tasks.required_skills
        FROM tasks
        LEFT JOIN members
            ON tasks.member_id = members.id
        WHERE tasks.project_id = ?
        ORDER BY tasks.id ASC
    """, (project_id,))

    tasks = cursor.fetchall()

    connection.close()

    return tasks

def update_task(
    project_id,
    task_id,
    member_id,
    task_name,
    status,
    description,
    required_skills=None
):

    if isinstance(required_skills, (list, tuple, set)):
        required_skills = ", ".join(
            str(skill).strip()
            for skill in required_skills
            if str(skill).strip()
        )

    if not task_name or not task_name.strip():
        raise ValueError("Task name cannot be empty.")

    allowed_statuses = ["Pending", "In Progress", "Completed"]

    if status not in allowed_statuses:
        raise ValueError("Invalid task status.")

    connection = get_connection()
    cursor = connection.cursor()

    # Verify that the task belongs to this project.
    cursor.execute("""
        SELECT id
        FROM tasks
        WHERE id = ? AND project_id = ?
    """, (task_id, project_id))

    task = cursor.fetchone()

    if task is None:
        connection.close()
        raise ValueError("Task does not belong to this project.")

    # Verify that the assigned member belongs to this project.
    cursor.execute("""
        SELECT id
        FROM members
        WHERE id = ? AND project_id = ?
    """, (member_id, project_id))

    member = cursor.fetchone()

    if member is None:
        connection.close()
        raise ValueError("Assigned member does not belong to this project.")

    cursor.execute("""
        UPDATE tasks
        SET
            member_id = ?,
            task_name = ?,
            status = ?,
            description = ?,
            required_skills = ?
        WHERE id = ? AND project_id = ?
    """, (
        member_id,
        task_name.strip(),
        status,
        description,
        required_skills,
        task_id,
        project_id
    ))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_rows

def convert_skills_to_list(skills):
    
    if not skills:
        return []

    return [
        skill.strip()
        for skill in str(skills).replace(";", ",").split(",")
        if skill.strip()
    ]


def update_member_workload(member_id, workload):

    allowed_workloads = ["Low", "Medium", "High", "Unknown"]

    if workload not in allowed_workloads:
        raise ValueError(
            "Workload must be Low, Medium, High or Unknown."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE members
        SET current_workload = ?
        WHERE id = ?
    """, (workload, member_id))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_rows


def get_members_for_takeover(project_id, departing_member_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, member_name, role, skills, current_workload
        FROM members
        WHERE project_id = ? AND id != ?
    """, (project_id, departing_member_id))

    members = cursor.fetchall()

    result = []

    for member in members:

        member_id, name, role, skills, workload = member

        cursor.execute("""
            SELECT task_name, status
            FROM tasks
            WHERE project_id = ? AND member_id = ?
        """, (project_id, member_id))

        tasks = cursor.fetchall()

        responsibilities = [
            task_name
            for task_name, status in tasks
            if (status or "").strip().lower()
            not in ["completed", "complete", "done", "closed"]
        ]

        result.append({
            "member_id": member_id,
            "name": name,
            "role": role,
            "skills": convert_skills_to_list(skills),
            "current_workload": workload or "Unknown",
            "current_responsibilities": responsibilities
        })

    connection.close()

    return result


def get_tasks_for_takeover(project_id, departing_member_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, task_name, status, description, required_skills
        FROM tasks
        WHERE project_id = ? AND member_id = ?
    """, (project_id, departing_member_id))

    tasks = cursor.fetchall()

    result = []

    for task in tasks:

        task_id, task_name, status, description, required_skills = task

        if (status or "").strip().lower() in [
            "completed", "complete", "done", "closed"
        ]:
            continue

        result.append({
            "task_id": task_id,
            "task": task_name,
            "status": status,
            "description": description,
            "required_skills": convert_skills_to_list(required_skills)
        })

    connection.close()

    return result

def update_task(
    project_id,
    task_id,
    member_id,
    task_name,
    status,
    description,
    required_skills=None
):

    if isinstance(required_skills, (list, tuple, set)):
        required_skills = ", ".join(
            str(skill).strip()
            for skill in required_skills
            if str(skill).strip()
        )

    if not task_name or not task_name.strip():
        raise ValueError("Task name cannot be empty.")

    allowed_statuses = ["Pending", "In Progress", "Completed"]

    if status not in allowed_statuses:
        raise ValueError("Invalid task status.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id FROM tasks
        WHERE id = ? AND project_id = ?
    """, (task_id, project_id))

    if cursor.fetchone() is None:
        connection.close()
        raise ValueError("Task not found in this project.")

    cursor.execute("""
        SELECT id FROM members
        WHERE id = ? AND project_id = ?
    """, (member_id, project_id))

    if cursor.fetchone() is None:
        connection.close()
        raise ValueError("Member does not belong to this project.")

    cursor.execute("""
        UPDATE tasks
        SET member_id = ?,
            task_name = ?,
            status = ?,
            description = ?,
            required_skills = ?
        WHERE id = ? AND project_id = ?
    """, (
        member_id,
        task_name.strip(),
        status,
        description,
        required_skills,
        task_id,
        project_id
    ))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_rows


# ==================================
# PROJECT UPDATE MANAGEMENT
# ==================================

def add_update(project_id, member_id, update_text):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO updates (project_id, member_id, update_text)
        VALUES (?, ?, ?)
    """, (project_id, member_id, update_text))

    update_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return update_id


def get_project_updates(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM updates
        WHERE project_id = ?
        ORDER BY created_at ASC, id ASC
    """, (project_id,))

    updates = cursor.fetchall()

    connection.close()

    return updates


# ==================================
# DECISION MANAGEMENT
# ==================================

def add_decision(project_id, decision_title, decision_description):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO decisions (
            project_id,
            decision_title,
            decision_description
        )
        VALUES (?, ?, ?)
    """, (project_id, decision_title, decision_description))

    decision_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return decision_id


def get_project_decisions(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM decisions
        WHERE project_id = ?
    """, (project_id,))

    decisions = cursor.fetchall()

    connection.close()

    return decisions


# ==================================
# DOCUMENT MANAGEMENT
# ==================================

def add_document(project_id, file_name, file_path):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO documents (project_id, file_name, file_path)
        VALUES (?, ?, ?)
    """, (project_id, file_name, file_path))

    document_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return document_id


def get_project_documents(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM documents
        WHERE project_id = ?
    """, (project_id,))

    documents = cursor.fetchall()

    connection.close()

    return documents


def update_member_skills(member_id, skills):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE members
        SET skills = ?
        WHERE id = ?
    """, (skills, member_id))

    conn.commit()
    conn.close()


def get_project_skills(project_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT member_name, role, skills
        FROM members
        WHERE project_id = ?
    """, (project_id,))

    skills = cursor.fetchall()

    conn.close()

    return skills


# ==================================
# PROJECT HISTORY MANAGEMENT
# ==================================

def get_project_history(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Get project details
    cursor.execute("""
        SELECT * FROM projects
        WHERE id = ?
    """, (project_id,))

    project = cursor.fetchone()

    if project is None:
        connection.close()
        return None

    # Get team members
    cursor.execute("""
        SELECT member_name, role, skills
        FROM members
        WHERE project_id = ?
    """, (project_id,))

    members = cursor.fetchall()

    # Get tasks with assigned member names
    cursor.execute("""
        SELECT
            tasks.task_name,
            tasks.status,
            tasks.description,
            members.member_name
        FROM tasks
        LEFT JOIN members ON tasks.member_id = members.id
        WHERE tasks.project_id = ?
        ORDER BY tasks.id ASC
    """, (project_id,))

    tasks = cursor.fetchall()

    # Get chronological updates
    cursor.execute("""
        SELECT
            updates.update_text,
            updates.created_at,
            members.member_name
        FROM updates
        LEFT JOIN members ON updates.member_id = members.id
        WHERE updates.project_id = ?
        ORDER BY updates.created_at ASC, updates.id ASC
    """, (project_id,))

    updates = cursor.fetchall()

    # Get project decisions
    cursor.execute("""
        SELECT
            decision_title,
            decision_description,
            created_at
        FROM decisions
        WHERE project_id = ?
        ORDER BY created_at ASC, id ASC
    """, (project_id,))

    decisions = cursor.fetchall()

    # Get uploaded documents
    cursor.execute("""
        SELECT file_name, file_path, uploaded_at
        FROM documents
        WHERE project_id = ?
        ORDER BY uploaded_at ASC, id ASC
    """, (project_id,))

    documents = cursor.fetchall()

    connection.close()

    return {
        "project": project,
        "members": members,
        "tasks": tasks,
        "updates": updates,
        "decisions": decisions,
        "documents": documents
    }


# ==================================
# UPDATE TEAM MEMBER DETAILS
# ==================================

def update_member(member_id, member_name, role, email, skills):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE members
        SET name = ?,
            member_name = ?,
            role = ?,
            email = ?,
            skills = ?
        WHERE id = ?
    """, (member_name, member_name, role, email, skills, member_id))

    connection.commit()

    updated_rows = cursor.rowcount

    connection.close()

    return updated_rows


# ==================================
# TAKEOVER RECOMMENDATION MANAGEMENT
# ==================================

def add_takeover_recommendation(
    project_id,
    task_id,
    departing_member_id,
    recommended_member_id,
    reason
):

    connection = get_connection()
    cursor = connection.cursor()

    # Verify task belongs to project
    cursor.execute("""
        SELECT id FROM tasks
        WHERE id = ? AND project_id = ?
    """, (task_id, project_id))

    task = cursor.fetchone()

    # Verify departing member
    cursor.execute("""
        SELECT id FROM members
        WHERE id = ? AND project_id = ?
    """, (departing_member_id, project_id))

    departing_member = cursor.fetchone()

    # Verify recommended member
    cursor.execute("""
        SELECT id FROM members
        WHERE id = ? AND project_id = ?
    """, (recommended_member_id, project_id))

    recommended_member = cursor.fetchone()

    if not task or not departing_member or not recommended_member:
        connection.close()
        raise ValueError("Task or member does not belong to this project.")

    cursor.execute("""
        INSERT INTO takeover_recommendations (
            project_id,
            task_id,
            departing_member_id,
            recommended_member_id,
            reason
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        project_id,
        task_id,
        departing_member_id,
        recommended_member_id,
        reason
    ))

    recommendation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return recommendation_id


def get_takeover_recommendations(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            takeover_recommendations.id,
            tasks.task_name,
            departing.member_name,
            recommended.member_name,
            takeover_recommendations.reason,
            takeover_recommendations.status,
            takeover_recommendations.created_at

        FROM takeover_recommendations

        JOIN tasks
            ON takeover_recommendations.task_id = tasks.id

        JOIN members AS departing
            ON takeover_recommendations.departing_member_id = departing.id

        JOIN members AS recommended
            ON takeover_recommendations.recommended_member_id = recommended.id

        WHERE takeover_recommendations.project_id = ?

        ORDER BY takeover_recommendations.created_at ASC,
                 takeover_recommendations.id ASC
    """, (project_id,))

    recommendations = cursor.fetchall()

    connection.close()

    return recommendations


# ==================================
# LEADER CORRECTION MANAGEMENT
# ==================================

def add_leader_correction(
    recommendation_id,
    corrected_member_id,
    correction_note
):

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether recommendation exists
    cursor.execute("""
        SELECT project_id
        FROM takeover_recommendations
        WHERE id = ?
    """, (recommendation_id,))

    recommendation = cursor.fetchone()

    if recommendation is None:
        connection.close()
        raise ValueError("Recommendation not found.")

    project_id = recommendation[0]

    # Verify corrected member belongs to project
    cursor.execute("""
        SELECT id FROM members
        WHERE id = ? AND project_id = ?
    """, (corrected_member_id, project_id))

    member = cursor.fetchone()

    if member is None:
        connection.close()
        raise ValueError("Corrected member does not belong to this project.")

    # Save correction
    cursor.execute("""
        INSERT INTO leader_corrections (
            recommendation_id,
            corrected_member_id,
            correction_note
        )
        VALUES (?, ?, ?)
    """, (
        recommendation_id,
        corrected_member_id,
        correction_note
    ))

    correction_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return correction_id


def get_leader_corrections(recommendation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            leader_corrections.id,
            leader_corrections.recommendation_id,
            members.member_name,
            leader_corrections.correction_note,
            leader_corrections.corrected_at

        FROM leader_corrections

        JOIN members
            ON leader_corrections.corrected_member_id = members.id

        WHERE leader_corrections.recommendation_id = ?

        ORDER BY leader_corrections.corrected_at ASC,
                 leader_corrections.id ASC
    """, (recommendation_id,))

    corrections = cursor.fetchall()

    connection.close()

    return corrections


# ==================================
# HANDOVER APPROVAL MANAGEMENT
# ==================================

def update_takeover_status(recommendation_id, status):

    if not isinstance(status, str):
        raise ValueError("Invalid status.")

    valid_statuses = ["Pending", "Approved", "Rejected"]

    status = status.strip().capitalize()

    if status not in valid_statuses:
        raise ValueError("Status must be Pending, Approved or Rejected.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE takeover_recommendations
        SET status = ?
        WHERE id = ?
    """, (status, recommendation_id))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    if updated_rows == 0:
        raise ValueError("Takeover recommendation not found.")

    return status


# ==================================
# HANDOVER REPORT MANAGEMENT
# ==================================

def add_handover_report(
    project_id,
    departing_member_id,
    report_content,
    incoming_member_guide
):

    if not isinstance(report_content, str) or not report_content.strip():
        raise ValueError("Handover report cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    # Verify project exists
    cursor.execute("""
        SELECT id FROM projects
        WHERE id = ?
    """, (project_id,))

    project = cursor.fetchone()

    if project is None:
        connection.close()
        raise ValueError("Project not found.")

    # Verify departing member belongs to project
    cursor.execute("""
        SELECT id FROM members
        WHERE id = ? AND project_id = ?
    """, (departing_member_id, project_id))

    member = cursor.fetchone()

    if member is None:
        connection.close()
        raise ValueError("Departing member does not belong to this project.")

    # Save report
    cursor.execute("""
        INSERT INTO handover_reports (
            project_id,
            departing_member_id,
            report_content,
            incoming_member_guide
        )
        VALUES (?, ?, ?, ?)
    """, (
        project_id,
        departing_member_id,
        report_content,
        incoming_member_guide
    ))

    report_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return report_id


def get_handover_reports(project_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            handover_reports.id,
            projects.project_name,
            members.member_name,
            handover_reports.report_content,
            handover_reports.incoming_member_guide,
            handover_reports.approval_status,
            handover_reports.created_at,
            handover_reports.approved_at

        FROM handover_reports

        JOIN projects
            ON handover_reports.project_id = projects.id

        JOIN members
            ON handover_reports.departing_member_id = members.id

        WHERE handover_reports.project_id = ?

        ORDER BY handover_reports.created_at ASC,
                 handover_reports.id ASC
    """, (project_id,))

    reports = cursor.fetchall()

    connection.close()

    return reports


def update_handover_report_status(report_id, status):

    if not isinstance(status, str):
        raise ValueError("Invalid approval status.")

    valid_statuses = ["Pending", "Approved", "Rejected"]

    status = status.strip().capitalize()

    if status not in valid_statuses:
        raise ValueError("Status must be Pending, Approved or Rejected.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE handover_reports
        SET approval_status = ?,
            approved_at = CASE
                WHEN ? = 'Approved' THEN CURRENT_TIMESTAMP
                ELSE NULL
            END
        WHERE id = ?
    """, (status, status, report_id))

    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    if updated_rows == 0:
        raise ValueError("Handover report not found.")

    return status

def get_tasks_for_takeover(project_id, departing_member_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, task_name, status, description, required_skills
        FROM tasks
        WHERE project_id = ? AND member_id = ?
    """, (project_id, departing_member_id))

    tasks = cursor.fetchall()
    connection.close()

    result = []

    for task in tasks:

        task_id, task_name, status, description, required_skills = task

        if (status or "").strip().lower() in [
            "completed", "complete", "done", "closed"
        ]:
            continue

        if isinstance(required_skills, str):
            skills = [
                skill.strip()
                for skill in required_skills.replace(";", ",").split(",")
                if skill.strip()
            ]
        else:
            skills = []

        result.append({
            "task_id": task_id,
            "task": task_name,
            "status": status,
            "description": description,
            "required_skills": skills
        })

    return result
