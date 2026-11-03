import streamlit as st
from datetime import date
import db_operations

st.title("Create New Project")
st.caption("Start building your project's knowledge workspace.")

st.divider()

st.subheader("Project Information")

with st.form("create_project_form"):

    project_name = st.text_input(
        "Project Name *",
        placeholder="e.g. Smart Campus Management System"
    )

    project_description = st.text_area(
        "Project Description *",
        placeholder="Briefly describe your project...",
        height=120
    )

    col1, col2 = st.columns(2)

    with col1:
        domain = st.selectbox(
            "Project Domain",
            [
                "Artificial Intelligence",
                "Data Science",
                "Web Development",
                "Mobile Application",
                "Cybersecurity",
                "Other"
            ]
        )

    with col2:
        start_date = st.date_input(
            "Project Start Date",
            value=date.today()
        )

    st.divider()

    st.subheader("Team Information")

    team_leader = st.text_input(
        "Project Leader",
        placeholder="Enter team leader's name"
    )

    team_members = st.text_area(
        "Team Members",
        placeholder="Enter member names separated by commas"
    )

    submitted = st.form_submit_button(
        "Create Project",
        use_container_width=True
    )

    if submitted:

        if not project_name.strip() or not project_description.strip():

            st.error("Please fill in all required fields.")

        else:

            try:
                # 1. Save project in SQLite
                project_id = db_operations.create_project(
                    project_name=project_name.strip(),
                    description=project_description.strip(),
                    domain=domain,
                    start_date=start_date.isoformat(),
                    status="Active"
                )

                # 2. Save project leader
                leader = team_leader.strip()

                if leader:

                    db_operations.add_member(
                        project_id=project_id,
                        member_name=leader,
                        role="Project Leader"
                    )

                # 3. Save other team members
                member_names = [
                    name.strip()
                    for name in team_members.split(",")
                    if name.strip()
                ]

                for member_name in member_names:

                    # Avoid adding the leader twice
                    if leader and member_name.lower() == leader.lower():
                        continue

                    db_operations.add_member(
                        project_id=project_id,
                        member_name=member_name,
                        role="Team Member"
                    )

                st.success(
                    f"Project created successfully! Project ID: {project_id}"
                )

                st.toast("Your project workspace is ready!")

            except Exception as error:

                st.error(f"Could not create project: {error}")