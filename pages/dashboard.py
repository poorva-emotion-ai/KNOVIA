import streamlit as st
import db_operations

st.title("Welcome to KNOVIA 👋")
st.caption("Where Knowledge Never Leaves.")
st.write("Manage your projects, track progress and explore AI-powered insights.")

# Retrieve projects from SQLite
try:
    projects = db_operations.get_projects_for_dashboard()
except Exception as error:
    st.error(f"Unable to load projects: {error}")
    st.stop()

# Calculate dashboard statistics
total = len(projects)

active = sum(
    1 for p in projects
    if (p.get("status") or "").lower() == "active"
)

completed = sum(
    1 for p in projects
    if (p.get("status") or "").lower() == "completed"
)

in_progress = sum(
    1 for p in projects
    if (p.get("status") or "").lower() == "in progress"
)

st.divider()
st.subheader("Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Projects", total)
col2.metric("Active Projects", active)
col3.metric("In Progress", in_progress)
col4.metric("Completed", completed)

st.divider()
st.subheader("Your Projects")

if projects:

    for project in projects:

        with st.container(border=True):

            st.markdown(f"### 📁 {project['name']}")
            st.write(project["description"])

            col1, col2 = st.columns(2)

            with col1:
                st.caption(f"Domain: {project['domain'] or 'Not specified'}")
                st.caption(
                    f"Start Date: {project['start_date'] or 'Not specified'}"
                )

            with col2:
                st.success(project["status"] or "Active")

                st.caption(
                    f"Project ID: {project['id']}"
                )

else:
    st.info("No projects yet. Create your first project to get started!")

st.divider()
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("＋ Create Project", use_container_width=True):
        st.switch_page("pages/create_project.py")

with col2:
    if st.button("↑ Upload Documents", use_container_width=True):
        st.switch_page("pages/document_upload.py")

with col3:
    if st.button("View Analysis", use_container_width=True):
        st.switch_page("pages/project_analysis.py")