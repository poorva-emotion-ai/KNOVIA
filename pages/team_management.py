import streamlit as st

from db_operations import (
    get_projects_for_dashboard,
    get_project_members,
    get_project_tasks,
    update_member_skills,
    update_member_workload,
    add_task,
    add_member,
    update_task
)

from db_operations import (
    get_projects_for_dashboard,
    get_project_members,
    get_project_tasks,
    update_member_skills,
    update_member_workload,
    add_task,
    add_member,
    update_task
)

from db_operations import (
    get_projects_for_dashboard,
    get_project_members,
    get_project_tasks,
    update_member_skills,
    update_member_workload,
    add_task,
    add_member
)

st.title("Team Management")
st.caption(
    "Manage team skills, workloads and task responsibilities "
    "for accurate AI takeover recommendations."
)

st.divider()


# --------------------------------------------------
# 1. LOAD PROJECTS
# --------------------------------------------------

projects = get_projects_for_dashboard()

if not projects:
    st.info("No projects found. Please create a project first.")
    st.stop()

project_options = {
    f"{project['name']} (ID: {project['id']})": project
    for project in projects
}

selected_project_label = st.selectbox(
    "Select Project",
    options=list(project_options.keys())
)

project = project_options[selected_project_label]
project_id = int(project["id"])

st.success(f"Selected project: {project['name']}")


# --------------------------------------------------
# 2. LOAD TEAM MEMBERS
# --------------------------------------------------

# --------------------------------------------------
# 2. ADD NEW TEAM MEMBER
# --------------------------------------------------

st.divider()
st.subheader("Add New Team Member")

with st.form("add_team_member_form", clear_on_submit=True):

    new_member_name = st.text_input(
        "Member Name",
        placeholder="Enter full name"
    )

    new_member_role = st.text_input(
        "Role / Responsibility",
        value="Team Member",
        placeholder="Example: Backend Developer"
    )

    new_member_email = st.text_input(
        "Email Address (Optional)",
        placeholder="member@example.com"
    )

    add_member_button = st.form_submit_button(
        "Add Team Member",
        type="primary",
        use_container_width=True
    )

    if add_member_button:

        if not new_member_name.strip():
            st.error("Please enter the member's name.")

        elif not new_member_role.strip():
            st.error("Please enter the member's role.")

        else:

            current_members = get_project_members(project_id)

            already_exists = any(
                (member[5] or member[2]).strip().lower()
                == new_member_name.strip().lower()
                for member in current_members
            )

            if already_exists:

                st.warning(
                    "This member already exists in the project."
                )

            else:

                try:

                    new_member_id = add_member(
                        project_id=project_id,
                        member_name=new_member_name.strip(),
                        role=new_member_role.strip(),
                        email=new_member_email.strip() or None
                    )

                    st.success(
                        f"Member added successfully! "
                        f"Member ID: {new_member_id}"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to add member: {error}"
                    )



members = get_project_members(project_id)

if not members:
    st.warning("This project has no registered team members.")
    st.stop()

member_records = {}

for member in members:
    member_id = int(member[0])

    member_records[member_id] = {
        "name": member[5] or member[2],
        "role": member[3],
        "skills": member[4] or "",
        "email": member[6] or "",
        "workload": (
            member[7] or "Unknown"
            if len(member) > 7
            else "Unknown"
        )
    }


# --------------------------------------------------
# CURRENT TEAM PROFILES
# --------------------------------------------------

st.divider()
st.subheader("Current Team Profiles")

profile_rows = []

for member_id, member in member_records.items():

    profile_rows.append({
        "ID": member_id,
        "Member Name": member["name"],
        "Role": member["role"],
        "Technical Skills": member["skills"] or "Not entered",
        "Current Workload": (
            member["workload"] or "Unknown"
        ).title()
    })

st.dataframe(
    profile_rows,
    hide_index=True,
    use_container_width=True
)



# --------------------------------------------------
# 3. UPDATE MEMBER SKILLS AND WORKLOAD
# --------------------------------------------------

st.divider()
st.subheader("Member Skills & Workload")

selected_member_id = st.selectbox(
    "Choose team member",
    options=list(member_records.keys()),
    format_func=lambda member_id: (
        f"{member_records[member_id]['name']} "
        f"({member_records[member_id]['role']})"
    )
)

selected_member = member_records[selected_member_id]

st.write(f"**Member:** {selected_member['name']}")
st.write(f"**Role:** {selected_member['role']}")

with st.form("member_profile_form"):

    skills_input = st.text_input(
        "Technical skills",
        value=selected_member["skills"],
        placeholder="Python, FastAPI, SQL, React"
    )

    st.caption(
        "Enter actual skills separated by commas. "
        "Do not add skills that the member has not confirmed."
    )

    workload_options = ["Low", "Medium", "High", "Unknown"]

    current_workload = selected_member["workload"].title()

    if current_workload not in workload_options:
        current_workload = "Unknown"

    workload = st.selectbox(
        "Current workload",
        options=workload_options,
        index=workload_options.index(current_workload)
    )

    update_profile = st.form_submit_button(
        "Save Member Information",
        type="primary",
        use_container_width=True
    )

    if update_profile:

        try:
            update_member_skills(
                selected_member_id,
                skills_input.strip()
            )

            update_member_workload(
                selected_member_id,
                workload
            )

            st.success(
                f"Information saved for {selected_member['name']}."
            )

            st.rerun()

        except Exception as error:
            st.error(f"Unable to update member: {error}")


# --------------------------------------------------
# 4. ADD TASKS
# --------------------------------------------------

st.divider()
st.subheader("Assign Project Tasks")

st.write(
    "Record each task, its owner, current status and required skills."
)

with st.form("add_task_form"):

    task_member_id = st.selectbox(
        "Assign task to",
        options=list(member_records.keys()),
        format_func=lambda member_id: member_records[member_id]["name"]
    )

    task_name = st.text_input(
        "Task name",
        placeholder="Example: Backend API Development"
    )

    task_status = st.selectbox(
        "Task status",
        options=["Pending", "In Progress", "Completed"]
    )

    task_description = st.text_area(
        "Task description",
        placeholder="Describe the actual work and expected result."
    )

    required_skills_input = st.text_input(
        "Required skills",
        placeholder="Python, FastAPI, REST API"
    )

    st.caption(
        "Enter only the skills genuinely required for this task."
    )

    save_task = st.form_submit_button(
        "Save Task",
        type="primary",
        use_container_width=True
    )

    if save_task:

        if not task_name.strip():
            st.error("Please enter a task name.")

        else:

            required_skills = [
                skill.strip()
                for skill in required_skills_input.split(",")
                if skill.strip()
            ]

            try:

                task_id = add_task(
                    project_id=project_id,
                    member_id=task_member_id,
                    task_name=task_name.strip(),
                    status=task_status,
                    description=task_description.strip(),
                    required_skills=required_skills
                )

                st.success(
                    f"Task saved successfully! Task ID: {task_id}"
                )

                st.rerun()

            except Exception as error:
                st.error(f"Unable to save task: {error}")



# --------------------------------------------------
# 5. EDIT EXISTING TASKS
# --------------------------------------------------

st.divider()
st.subheader("Edit Existing Task")

tasks = get_project_tasks(project_id)

if tasks:

    task_records = {
        int(task[0]): task
        for task in tasks
    }

    selected_task_id = st.selectbox(
        "Choose a task to edit",
        options=list(task_records.keys()),
        format_func=lambda task_id: (
            f"{task_records[task_id][4]} (ID: {task_id})"
        ),
        key="edit_task_selection"
    )

    selected_task = task_records[selected_task_id]

    member_ids = list(member_records.keys())

    current_member_id = selected_task[2]

    if current_member_id not in member_ids:
        current_member_id = member_ids[0]

    status_options = [
        "Pending",
        "In Progress",
        "Completed"
    ]

    current_status = str(
        selected_task[5] or "Pending"
    ).strip()

    status_lookup = {
        status.lower(): status
        for status in status_options
    }

    current_status = status_lookup.get(
        current_status.lower(),
        "Pending"
    )

    existing_skills = selected_task[7] or ""

    with st.form("edit_existing_task_form"):

        st.write(f"Editing Task ID: {selected_task_id}")

        edit_task_name = st.text_input(
            "Task Name",
            value=selected_task[4] or ""
        )

        edit_member_id = st.selectbox(
            "Assigned Member",
            options=member_ids,
            index=member_ids.index(current_member_id),
            format_func=lambda member_id: (
                member_records[member_id]["name"]
            )
        )

        edit_task_status = st.selectbox(
            "Task Status",
            options=status_options,
            index=status_options.index(current_status)
        )

        edit_description = st.text_area(
            "Task Description",
            value=selected_task[6] or ""
        )

        edit_required_skills = st.text_input(
            "Required Skills",
            value=existing_skills,
            help="Separate multiple skills with commas."
        )

        update_button = st.form_submit_button(
            "Update Task",
            type="primary",
            use_container_width=True
        )

        if update_button:

            if not edit_task_name.strip():

                st.error("Task name cannot be empty.")

            else:

                required_skills = [
                    skill.strip()
                    for skill in edit_required_skills.split(",")
                    if skill.strip()
                ]

                try:

                    updated_rows = update_task(
                        project_id=project_id,
                        task_id=selected_task_id,
                        member_id=edit_member_id,
                        task_name=edit_task_name.strip(),
                        status=edit_task_status,
                        description=edit_description.strip(),
                        required_skills=required_skills
                    )

                    if updated_rows:
                        st.success(
                            "Task updated successfully!"
                        )
                        st.rerun()
                    else:
                        st.warning("No task was updated.")

                except Exception as error:

                    st.error(
                        f"Unable to update task: {error}"
                    )

else:

    st.info("There are no tasks available to edit.")


# --------------------------------------------------
# 6. DISPLAY PROJECT TASKS
# --------------------------------------------------

st.divider()
st.subheader("Project Task Records")

tasks = get_project_tasks(project_id)

if tasks:

    for task in tasks:

        task_id = task[0]
        member_name = task[3] or "Unassigned"
        name = task[4]
        status = task[5]
        description = task[6]
        required_skills = task[7] or ""

        with st.expander(f"{name} — {status}"):

            st.write(f"**Task ID:** {task_id}")
            st.write(f"**Assigned Member:** {member_name}")
            st.write(f"**Status:** {status}")

            st.write(
                f"**Description:** "
                f"{description or 'Not specified'}"
            )

            st.write(
                f"**Required Skills:** "
                f"{required_skills or 'Not specified'}"
            )

else:

    st.info(
        "No tasks have been recorded for this project yet."
    )
