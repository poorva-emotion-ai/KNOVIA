
import streamlit as st

from db_operations import (
    get_projects_for_dashboard,
    get_handover_reports,
    update_handover_report_status
)


st.title("Reports & Handover Approval")

st.caption(
    "Review AI-generated handover reports and manage project leader approval."
)

st.divider()


# --------------------------------------------------
# 1. LOAD PROJECTS
# --------------------------------------------------

projects = get_projects_for_dashboard()

if not projects:
    st.info("No projects found. Create a project first.")
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
# 2. LOAD SAVED HANDOVER REPORTS
# --------------------------------------------------

st.divider()
st.subheader("Saved Handover Reports")

reports = get_handover_reports(project_id)

if not reports:
    st.info(
        "No handover reports are available for this project yet. "
        "Generate a report from the Member Exit page."
    )
    st.stop()


# --------------------------------------------------
# 3. DISPLAY REPORTS
# --------------------------------------------------

for report in reversed(reports):

    report_id = report[0]
    project_name = report[1]
    departing_member = report[2]
    report_content = report[3]
    incoming_guide = report[4]
    approval_status = report[5]
    created_at = report[6]
    approved_at = report[7]

    st.divider()

    with st.expander(
        f"Report #{report_id} — {departing_member} — {approval_status}",
        expanded=(approval_status == "Pending")
    ):

        st.write(f"**Project:** {project_name}")
        st.write(f"**Departing Member:** {departing_member}")
        st.write(f"**Report ID:** {report_id}")
        st.write(f"**Created At:** {created_at}")
        st.write(f"**Approval Status:** {approval_status}")

        if approved_at:
            st.write(f"**Approved At:** {approved_at}")

        st.divider()

        st.subheader("Complete Handover Report")
        st.text(report_content or "No report content available.")

        st.divider()

        st.subheader("Incoming Member Guide")
        st.text(incoming_guide or "No incoming member guide available.")

        st.divider()

        # --------------------------------------------------
        # 4. LEADER APPROVAL
        # --------------------------------------------------

        if approval_status == "Pending":

            st.warning(
                "This report is awaiting project leader approval."
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Approve Handover",
                    key=f"approve_{report_id}",
                    type="primary",
                    use_container_width=True
                ):

                    try:

                        update_handover_report_status(
                            report_id,
                            "Approved"
                        )

                        st.success(
                            f"Report #{report_id} approved successfully."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to approve report: {error}"
                        )

            with col2:

                if st.button(
                    "Reject Handover",
                    key=f"reject_{report_id}",
                    use_container_width=True
                ):

                    try:

                        update_handover_report_status(
                            report_id,
                            "Rejected"
                        )

                        st.warning(
                            f"Report #{report_id} rejected."
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to reject report: {error}"
                        )

        elif approval_status == "Approved":

            st.success("This handover report has been approved.")

        elif approval_status == "Rejected":

            st.error("This handover report has been rejected.")


st.divider()

st.caption(
    "Note: Approving a handover report does not automatically "
    "assign tasks to suggested team members. Final task assignment "
    "remains a separate human decision."
)
