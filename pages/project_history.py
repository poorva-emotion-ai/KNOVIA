
import streamlit as st
import db_operations

st.title("📚 Project History")
st.caption("Explore your project's documents, updates and activities.")

st.divider()

# ==========================================
# LOAD PROJECTS FROM SQLITE
# ==========================================

try:
    projects = db_operations.get_projects_for_dashboard()

except Exception as error:
    st.error(f"Unable to load projects: {error}")
    st.stop()

if not projects:
    st.info("No projects available. Please create a project first.")
    st.stop()

# Use project IDs because project names can be duplicated
project_options = {
    f"{project['name']} (ID: {project['id']})": project
    for project in projects
}

selected_label = st.selectbox(
    "Select Project",
    list(project_options.keys())
)

selected_project = project_options[selected_label]
project_id = selected_project["id"]

# ==========================================
# LOAD COMPLETE PROJECT HISTORY
# ==========================================

try:
    history = db_operations.get_project_history(project_id)

    if history is None:
        st.error("Project not found.")
        st.stop()

except Exception as error:
    st.error(f"Unable to load project history: {error}")
    st.stop()

# Project tuple:
# id, project_name, description, created_at,
# domain, start_date, status

project = history["project"]
members = history["members"]
tasks = history["tasks"]
updates = history["updates"]
decisions = history["decisions"]
documents = history["documents"]

# ==========================================
# PROJECT INFORMATION
# ==========================================

st.divider()
st.subheader("Project Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Project Name:**", project[1])
    st.write("**Description:**", project[2] or "Not specified")
    st.write("**Domain:**", project[4] or "Not specified")

with col2:
    st.write("**Start Date:**", project[5] or "Not specified")
    st.write("**Status:**", project[6] or "Active")
    st.write("**Project ID:**", project[0])

# ==========================================
# PROJECT STATISTICS
# ==========================================

st.divider()
st.subheader("Project Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Team Members", len(members))
col2.metric("Total Tasks", len(tasks))
col3.metric("Documents", len(documents))
col4.metric("Updates", len(updates))

# ==========================================
# TEAM MEMBERS
# ==========================================

st.divider()
st.subheader("👥 Team Members")

if members:

    for member in members:

        member_name, role, skills = member

        with st.container(border=True):

            st.write(f"**{member_name or 'Unnamed Member'}**")
            st.caption(f"Role: {role or 'Not specified'}")
            st.write(f"Skills: {skills or 'Not specified'}")

else:
    st.info("No team members added yet.")

# ==========================================
# TASK HISTORY
# ==========================================

st.divider()
st.subheader("📋 Project Tasks")

if tasks:

    for task in tasks:

        task_name, status, description, assigned_member = task

        with st.container(border=True):

            st.write(f"**{task_name}**")
            st.caption(f"Status: {status or 'Pending'}")

            st.write(
                f"Assigned Member: {assigned_member or 'Unassigned'}"
            )

            if description:
                st.write(description)

else:
    st.info("No tasks recorded for this project yet.")

# ==========================================
# UPLOADED DOCUMENTS
# ==========================================

st.divider()
st.subheader("📄 Uploaded Documents")

if documents:

    for document in documents:

        file_name, file_path, uploaded_at = document

        with st.container(border=True):

            st.write(f"**{file_name}**")
            st.caption(f"Uploaded: {uploaded_at}")

else:
    st.info("No documents uploaded yet.")

# ==========================================
# PROJECT UPDATES
# ==========================================

st.divider()
st.subheader("📝 Project Updates")

if updates:

    for update in reversed(updates):

        update_text, created_at, member_name = update

        with st.container(border=True):

            st.write(update_text)
            st.caption(
                f"Date: {created_at} | "
                f"Member: {member_name or 'Not specified'}"
            )

else:
    st.info("No project updates recorded yet.")

# ==========================================
# IMPORTANT DECISIONS
# ==========================================

st.divider()
st.subheader("📌 Important Decisions")

if decisions:

    for decision in reversed(decisions):

        decision_title, decision_description, created_at = decision

        with st.container(border=True):

            st.write(f"**{decision_title}**")
            st.write(decision_description or "No description provided.")
            st.caption(f"Date: {created_at}")

else:
    st.info("No important decisions recorded yet.")
    
# ==========================================
# DELETE PROJECT
# ==========================================

st.divider()
st.subheader("🗑️ Delete Project")

st.warning(
    f"You are managing: {project[1]} (Project ID: {project_id}). "
    "Deleting this project will remove its associated data."
)

if st.button(
    "🗑️ Delete Project",
    key=f"delete_project_{project_id}",
    use_container_width=True
):
    st.session_state[f"confirm_delete_{project_id}"] = True

# Show confirmation
if st.session_state.get(f"confirm_delete_{project_id}", False):

    st.error(
        f"Are you sure you want to delete '{project[1]}'? "
        "This action cannot be undone."
    )

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:

        if st.button(
            "Confirm Delete",
            key=f"confirm_button_{project_id}",
            type="primary",
            use_container_width=True
        ):

            try:
                from project_deletion import delete_project

                success, message = delete_project(project_id)

                if success:
                    st.success(message)
                    st.session_state.pop(
                        f"confirm_delete_{project_id}",
                        None
                    )
                    st.rerun()
                else:
                    st.error(message)

            except Exception as error:
                st.error(f"Deletion failed: {error}")

    with cancel_col:

        if st.button(
            "Cancel",
            key=f"cancel_button_{project_id}",
            use_container_width=True
        ):

            st.session_state.pop(
                f"confirm_delete_{project_id}",
                None
            )
            st.rerun()

