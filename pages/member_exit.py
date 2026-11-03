
import streamlit as st

from db_operations import (
    get_projects_for_dashboard,
    get_project_members,
    get_project_documents,
    get_tasks_for_takeover,
    get_members_for_takeover
)

from ai_engine.handover_report import generate_handover_report


st.title("Member Exit & Handover")
st.caption(
    "Generate an evidence-based handover when a project member leaves."
)

st.divider()


# --------------------------------------------------
# 1. LOAD PROJECTS FROM SQLITE
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
# 2. LOAD PROJECT MEMBERS
# --------------------------------------------------

st.divider()
st.subheader("Select Departing Member")

members = get_project_members(project_id)

if not members:
    st.warning("No members are registered in this project.")
    st.stop()

member_options = {}

for member in members:

    member_id = int(member[0])
    member_name = member[5] or member[2]
    role = member[3]

    member_options[member_id] = {
        "name": member_name,
        "role": role
    }

departing_member_id = st.selectbox(
    "Choose the member who is leaving",
    options=list(member_options.keys()),
    format_func=lambda member_id: (
        f"{member_options[member_id]['name']} "
        f"({member_options[member_id]['role']})"
    )
)

departing_member = member_options[departing_member_id]["name"]

st.info(f"Departing member: {departing_member}")


# --------------------------------------------------
# 3. LOAD PROJECT DOCUMENTS
# --------------------------------------------------

st.divider()
st.subheader("Select Project Documents")

documents = get_project_documents(project_id)

document_options = {
    int(document[0]): str(document[2])
    for document in documents
}

if document_options:

    selected_document_ids = st.multiselect(
        "Choose documents for AI analysis",
        options=list(document_options.keys()),
        default=list(document_options.keys()),
        format_func=lambda document_id: (
            f"{document_options[document_id]} "
            f"(ID: {document_id})"
        )
    )

    st.caption(
        "Only documents indexed in ChromaDB will be used "
        "for Gemini analysis."
    )

else:
    selected_document_ids = []

    st.warning(
        "No project documents are recorded. "
        "You can still generate a report, but document-based "
        "AI analysis will be unavailable."
    )


# --------------------------------------------------
# 4. SHOW ACTUAL UNFINISHED TASKS
# --------------------------------------------------

st.divider()
st.subheader("Recorded Unfinished Responsibilities")

unfinished_tasks = get_tasks_for_takeover(
    project_id,
    departing_member_id
)

if unfinished_tasks:

    for task in unfinished_tasks:

        st.markdown(f"**{task['task']}**")

        st.write(f"Task ID: {task['task_id']}")
        st.write(f"Status: {task['status']}")
        st.write(
            f"Required skills: "
            f"{', '.join(task['required_skills']) or 'Not specified'}"
        )

        st.divider()

else:
    st.info(
        "No unfinished tasks are currently recorded "
        "for this member."
    )


# --------------------------------------------------
# 5. GENERATE HANDOVER REPORT
# --------------------------------------------------

st.divider()
st.subheader("AI Handover Generation")

st.write(
    "KNOVIA will analyse the selected documents, retrieve "
    "the departing member's unfinished tasks, and identify "
    "potential takeover candidates from the remaining team."
)

generate_button = st.button(
    "Generate Handover Report",
    type="primary",
    use_container_width=True
)

if generate_button:

    try:

        with st.spinner(
            "Generating handover report using KNOVIA AI..."
        ):

            result = generate_handover_report(
                project_id=project_id,
                departing_member_id=departing_member_id,
                document_ids=selected_document_ids
            )

            result["selected_document_ids"] = selected_document_ids

            st.session_state["latest_handover_result"] = result

        st.success(
            f"Handover report generated successfully! "
            f"Report ID: {result['report_id']}"
        )

    except Exception as error:

        st.error("Unable to generate the handover report.")

        st.exception(error)


# --------------------------------------------------
# 6. DISPLAY GENERATED REPORT
# --------------------------------------------------

result = st.session_state.get("latest_handover_result")

if (
    result
    and result["project_id"] == project_id
    and result["departing_member_id"] == departing_member_id
):

    st.divider()
    st.subheader("Generated Handover Results")

    st.metric(
        "Handover Report ID",
        result["report_id"]
    )

    st.metric(
        "Saved Takeover Recommendations",
        len(result["saved_recommendation_ids"])
    )

    st.warning(
        "Approval Status: Pending. "
        "AI recommendations are suggestions only. "
        "The project leader must review them before assignment."
    )

    # Member exit analysis

    with st.expander("AI Member Exit Analysis", expanded=True):

        st.markdown(result["member_exit_analysis"])

    # Unfinished responsibilities

    with st.expander("Unfinished Responsibilities"):

        tasks = result["unfinished_responsibilities"]

        if tasks:

            for task in tasks:
                st.markdown(f"**{task['task']}**")
                st.write(f"Status: {task['status']}")
                st.write(
                    "Required skills: "
                    + (
                        ", ".join(task["required_skills"])
                        or "Not specified"
                    )
                )
                st.divider()

        else:
            st.info("No unfinished tasks were found.")

    # Takeover recommendations

    with st.expander("Suggested Takeover Candidates", expanded=True):

        recommendations = result["takeover_recommendations"]

        if recommendations:

            for index, recommendation in enumerate(
                recommendations,
                start=1
            ):

                candidate = recommendation["candidate"]
                work = recommendation["existing_work_details"]

                st.markdown(
                    f"### Candidate {index}: {candidate['name']}"
                )

                st.write(f"Task: {recommendation['task']}")

                st.write(
                    f"Skill match: "
                    f"{candidate['skill_match_percentage']}%"
                )

                st.progress(
                    candidate["skill_match_percentage"] / 100
                )

                st.write(
                    f"Match level: {candidate['skill_match_level']}"
                )

                st.write(
                    f"Current workload: {work['current_workload']}"
                )

                st.write(
                    "Existing responsibilities: "
                    + (
                        ", ".join(work["current_responsibilities"])
                        or "Not documented"
                    )
                )

                if recommendation["verification_needed"]:

                    st.warning(
                        "Verification needed: "
                        + "; ".join(
                            recommendation["verification_needed"]
                        )
                    )

                st.caption("Decision: Awaiting human approval")

                st.divider()

        
        else:

            st.info(
                "No suitable skill matches found. "
                "The leader must review the team manually."
            )

            st.markdown("#### Skill Gap Analysis")

            remaining_team = get_members_for_takeover(
                project_id,
                departing_member_id
            )

            for task in result["unfinished_responsibilities"]:

                required_skills = task.get("required_skills", [])

                st.markdown(f"**Task: {task['task']}**")

                if not required_skills:
                    st.warning(
                        "Required skills are not recorded "
                        "for this task."
                    )
                    continue

                st.write(
                    "Required skills: "
                    + ", ".join(required_skills)
                )

                any_match = False

                for member in remaining_team:

                    member_skills = member.get("skills", [])

                    matched = [
                        skill for skill in required_skills
                        if skill.lower() in {
                            item.lower() for item in member_skills
                        }
                    ]

                    if matched:
                        any_match = True

                    st.write(
                        f"**{member['name']}** — "
                        f"Skills: {', '.join(member_skills) or 'Not recorded'}"
                        f" | Workload: {member['current_workload']}"
                    )

                    if matched:
                        st.success(
                            "Matching skills: " + ", ".join(matched)
                        )

                    elif member["current_workload"].lower() == "high":
                        st.warning(
                            "No skill match recorded. "
                            "Member also has a high workload."
                        )

                if not any_match:
                    st.error(
                        "No remaining team member has a "
                        "recorded match for the required skills."
                    )

                st.divider()


    # Incoming member guide

    with st.expander("Incoming Member Guide"):

        st.text(result["incoming_member_guide"])

    # Complete report

    with st.expander("Full Handover Report"):

        st.text(result["report_content"])

    st.success(
        "Report saved in SQLite and awaiting project leader review."
    )

    st.info(
        "You can review and approve or reject this report "
        "from the Reports page once that page is integrated."
    )
